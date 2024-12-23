from transformers import AutoModelForMaskedLM
from transformers import AutoTokenizer
from datasets import load_dataset
from datasets import Dataset
import pandas as pd
from datasets import load_dataset
from transformers import AutoTokenizer
from transformers import DataCollatorForLanguageModeling
import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForMaskedLM
from torch.optim import AdamW
from accelerate import Accelerator
from transformers import get_scheduler
from transformers import default_data_collator
from tqdm.auto import tqdm
import math
import argparse

def main(args):
    model_checkpoint = "bert-base-cased"
    model = AutoModelForMaskedLM.from_pretrained(model_checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

    if args.aug_method == 'LLM':
        imdb_dataset = load_dataset("imdb")
        imdb_df = pd.read_csv('../counterfactual/augmented/imdb/imdb_augmented_LLM_data.csv')
        aug_ds = Dataset.from_dict({"text": imdb_dataset['train']['text'] + imdb_df['text'].tolist(), "label": imdb_dataset['train']['label'] + imdb_df['label'].tolist()})
        imdb_dataset['train'] = aug_ds

    if args.aug_method == 'ours':
        imdb_dataset = load_dataset("imdb")
        imdb_df = pd.read_csv('../counterfactual/augmented/imdb/imdb_augmented_ours_data.csv')
        aug_ds = Dataset.from_dict({"text": imdb_dataset['train']['text'] + imdb_df['text'].tolist(), "label": imdb_dataset['train']['label'] + imdb_df['label'].tolist()})
        imdb_dataset['train'] = aug_ds

    if args.aug_method == 'none':
        imdb_dataset = load_dataset("imdb")

    #define tokenize function to tokenize the dataset
    def tokenize_function(data):
        result = tokenizer(data["text"])
        return result

    # batched is set to True to activate fast multithreading!
    tokenize_dataset = imdb_dataset.map(tokenize_function, batched = True, remove_columns = ["text", "label"])

    def group_texts(data):
        chunk_size = 300
        # concatenate texts
        concatenated_sequences = {k: sum(data[k], []) for k in data.keys()}
        #compute length of concatenated texts
        total_concat_length = len(concatenated_sequences[list(data.keys())[0]])

        # drop the last chunk if is smaller than the chunk size
        total_length = (total_concat_length // chunk_size) * chunk_size

        # split the concatenated sentences into chunks using the total length
        result = {k: [t[i: i + chunk_size] for i in range(0, total_length, chunk_size)]
        for k, t in concatenated_sequences.items()}

        '''we create a new labels column which is a copy of the input_ids of the processed text data, 
        we need to predict randomly masked tokens in the input batch and the labels column serve as 
        ground truth for our masked language model to learn from. '''
        
        result["labels"] = result["input_ids"].copy()

        return result

    processed_dataset = tokenize_dataset.map(group_texts, batched = True)

    ''' Downsample the dataset to 10000 samples for training to for low gpu consumption'''
    train_size = 30000

    # test dataset is 10 % of the 10000 samples selected which is 1000
    test_size = int(0.01 * train_size)

    downsampled_dataset = processed_dataset["train"].train_test_split(train_size=train_size, test_size=test_size, seed=42)

    ''' Apply random masking once on the whole test data, then uses the default data collector to handle the test dataset in batches '''

    data_collator = DataCollatorForLanguageModeling(tokenizer = tokenizer, mlm_probability = 0.15)

    # we shall insert mask randomly in the sentence
    def insert_random_mask(batch):
        features = [dict(zip(batch, t)) for t in zip(*batch.values())]
        masked_inputs = data_collator(features)
        # Create a new "masked" column for each column in the dataset
        return {"masked_" + k: v.numpy() for k, v in masked_inputs.items()}

    ''' we drop the unmasked columns in the test dataset and replace them with the masked ones '''

    eval_dataset = downsampled_dataset["test"].map(
        insert_random_mask,
        batched=True,
        remove_columns=downsampled_dataset["test"].column_names,
    )
    eval_dataset = eval_dataset.rename_columns(
        {
            "masked_input_ids": "input_ids",
            "masked_attention_mask": "attention_mask",
            "masked_token_type_ids": "token_type_ids",
            "masked_labels": "labels",
        }
    )

    # set batch size to 32, a larger bacth size when using a more powerful gpu
    batch_size = 64

    # load the train dataset for traing
    train_dataloader = DataLoader(downsampled_dataset["train"], shuffle=True, batch_size=batch_size, collate_fn=data_collator,)

    # load the test dataset for evaluation
    eval_dataloader = DataLoader(eval_dataset, batch_size=batch_size, collate_fn=default_data_collator)

    # initialize pretrained bert model
    model = AutoModelForMaskedLM.from_pretrained(model_checkpoint)

    # set the optimizer
    optimizer = AdamW(model.parameters(), lr=5e-5)

    # initialize accelerator for training
    accelerator = Accelerator()
    model, optimizer, train_dataloader, eval_dataloader = accelerator.prepare(model, optimizer, train_dataloader, eval_dataloader)

    # set the number of epochs which is set to 30
    num_train_epochs = 30
    num_update_steps_per_epoch = len(train_dataloader)
    num_training_steps = num_train_epochs * num_update_steps_per_epoch

    # define the learning rate scheduler for training
    lr_scheduler = get_scheduler("linear",optimizer=optimizer,num_warmup_steps=0,num_training_steps=num_training_steps)


    progress_bar = tqdm(range(num_training_steps))

    model_name = f"{args.aug_method}_mlm"
    output_dir = f"/nas_homes/kyohoon1/counterfactual/model_checkpoint/imdb/mlm/{args.aug_method}_mlm"

    model.to('cuda')

    for epoch in range(num_train_epochs):
        # Training
        model.train()
        for batch in train_dataloader:
            outputs = model(**batch)
            loss = outputs.loss
            accelerator.backward(loss)

            optimizer.step()
            lr_scheduler.step()
            optimizer.zero_grad()
            progress_bar.update(1)

        # Evaluation
        model.eval()
        losses = []
        for step, batch in enumerate(eval_dataloader):
            with torch.no_grad():
                outputs = model(**batch)

            loss = outputs.loss
            losses.append(accelerator.gather(loss.repeat(batch_size)))

        losses = torch.cat(losses)
        losses = losses[: len(eval_dataset)]

        # perplexity metric used for mask language model training
        try:
            perplexity = math.exp(torch.mean(losses))
        except OverflowError:
            perplexity = float("inf")

        print(f">>> Epoch {epoch}: Perplexity: {perplexity}")

        # Save model
        accelerator.wait_for_everyone()
        unwrapped_model = accelerator.unwrap_model(model)
        unwrapped_model.save_pretrained(output_dir, save_function=accelerator.save)
        if accelerator.is_main_process:
            tokenizer.save_pretrained(output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing Method')
    parser.add_argument('--aug_method', default='none', type=str, help='')
    args = parser.parse_args()

    main(args)