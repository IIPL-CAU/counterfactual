import os
import json
import torch
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tqdm.auto import tqdm

from datasets import load_dataset

def data_split_index(seq, valid_ratio: float = 0.1, test_ratio: float = 0.03):

    paired_data_len = len(seq)
    valid_num = int(paired_data_len * valid_ratio)
    test_num = int(paired_data_len * test_ratio)

    valid_index = np.random.choice(paired_data_len, valid_num, replace=False)
    train_index = list(set(range(paired_data_len)) - set(valid_index))
    test_index = np.random.choice(train_index, test_num, replace=False)
    train_index = list(set(train_index) - set(test_index))

    return train_index, valid_index, test_index

def data_load(args):

    src_list = dict()
    trg_list = dict()

    if args.data_name == 'imdb':
        dataset = load_dataset("imdb")

        train_dat = dataset['train']
        test_dat = dataset['test']

        train_index, valid_index, test_index = data_split_index(train_dat, valid_ratio=args.valid_ratio, test_ratio=0)

        src_list['train'] = np.array(train_dat['text'])[train_index]
        src_list['train2'] = None
        trg_list['train'] = np.array(train_dat['label'])[train_index]

        src_list['valid'] = np.array(train_dat['text'])[valid_index]
        src_list['valid2'] = None
        trg_list['valid'] = np.array(train_dat['label'])[valid_index]

        src_list['test'] = test_dat['text']
        src_list['test2'] = None
        trg_list['test'] = test_dat['label']

    if args.data_name == 'sst2':
        dataset = load_dataset("glue", args.data_name)
        train_dat = pd.DataFrame(dataset['train'])
        valid_dat = pd.DataFrame(dataset['validation'])
        test_dat = pd.DataFrame(dataset['test'])

        src_list['train'] = np.array(train_dat['sentence'])
        src_list['train2'] = None
        trg_list['train'] = np.array(train_dat['label'])

        src_list['valid'] = np.array(valid_dat['sentence'])
        src_list['valid2'] = None
        trg_list['valid'] = np.array(valid_dat['label'])

        src_list['test'] = np.array(test_dat['sentence'])
        src_list['test2'] = None
        trg_list['test'] = np.array(test_dat['label'])

    if args.data_name == 'cola':
        dataset = load_dataset("glue", args.data_name)
        train_dat = pd.DataFrame(dataset['train'])
        valid_dat = pd.DataFrame(dataset['validation'])
        test_dat = pd.DataFrame(dataset['test'])

        src_list['train'] = np.array(train_dat['sentence'])
        src_list['train2'] = None
        trg_list['train'] = np.array(train_dat['label'])

        src_list['valid'] = np.array(valid_dat['sentence'])
        src_list['valid2'] = None
        trg_list['valid'] = np.array(valid_dat['label'])

        src_list['test'] = np.array(test_dat['sentence'])
        src_list['test2'] = None
        trg_list['test'] = np.array(test_dat['label'])

    if args.data_name == 'ag_news':
        dataset = load_dataset("ag_news")

        train_dat = dataset['train']
        test_dat = dataset['test']

        train_index, valid_index, test_index = data_split_index(train_dat, valid_ratio=args.valid_ratio, test_ratio=0)

        src_list['train'] = np.array(train_dat['text'])[train_index]
        src_list['train2'] = None
        trg_list['train'] = np.array(train_dat['label'])[train_index]

        src_list['valid'] = np.array(train_dat['text'])[valid_index]
        src_list['valid2'] = None
        trg_list['valid'] = np.array(train_dat['label'])[valid_index]

        src_list['test'] = test_dat['text']
        src_list['test2'] = None
        trg_list['test'] = test_dat['label']

    if args.data_name == 'ag_news':
        dataset = load_dataset("ag_news")

        train_dat = dataset['train']
        test_dat = dataset['test']

        train_index, valid_index, test_index = data_split_index(train_dat, valid_ratio=args.valid_ratio, test_ratio=0)

        src_list['train'] = np.array(train_dat['text'])[train_index]
        src_list['train2'] = None
        trg_list['train'] = np.array(train_dat['label'])[train_index]

        src_list['valid'] = np.array(train_dat['text'])[valid_index]
        src_list['valid2'] = None
        trg_list['valid'] = np.array(train_dat['label'])[valid_index]

        src_list['test'] = test_dat['text']
        src_list['test2'] = None
        trg_list['test'] = test_dat['label']

    if args.data_name == 'mnli':
        dataset = load_dataset("glue", args.data_name)
        train_dat = pd.DataFrame(dataset['train'])
        valid_dat = pd.DataFrame(dataset['validation_matched'])
        test_dat = pd.DataFrame(dataset['test_matched'])

        src_list['train'] = train_dat['premise'].tolist()
        src_list['train2'] = train_dat['hypothesis'].tolist()
        trg_list['train'] = train_dat['label'].tolist()

        src_list['valid'] = valid_dat['premise'].tolist()
        src_list['valid2'] = valid_dat['hypothesis'].tolist()
        trg_list['valid'] = valid_dat['label'].tolist()

        src_list['test'] = test_dat['premise'].tolist()
        src_list['test2'] = test_dat['hypothesis'].tolist()
        trg_list['test'] = test_dat['label'].tolist()

    if args.data_name == 'snli':
        dataset = load_dataset("stanfordnlp/snli")
        train_dat = pd.DataFrame(dataset['train'])
        valid_dat = pd.DataFrame(dataset['validation'])
        test_dat = pd.DataFrame(dataset['test'])

        train_dat = train_dat[train_dat.label != -1]
        valid_dat = valid_dat[valid_dat.label != -1]
        test_dat = test_dat[test_dat.label != -1]

        src_list['train'] = train_dat['premise'].tolist()
        src_list['train2'] = train_dat['hypothesis'].tolist()
        trg_list['train'] = train_dat['label'].tolist()

        src_list['valid'] = valid_dat['premise'].tolist()
        src_list['valid2'] = valid_dat['hypothesis'].tolist()
        trg_list['valid'] = valid_dat['label'].tolist()

        src_list['test'] = test_dat['premise'].tolist()
        src_list['test2'] = test_dat['hypothesis'].tolist()
        trg_list['test'] = test_dat['label'].tolist()

    if args.data_name == 'mrpc':
        dataset = load_dataset("glue", args.data_name)
        train_dat = pd.DataFrame(dataset['train'])
        valid_dat = pd.DataFrame(dataset['validation_matched'])
        test_dat = pd.DataFrame(dataset['test_matched'])

        src_list['train'] = train_dat['sentence1'].tolist()
        src_list['train2'] = train_dat['sentence2'].tolist()
        trg_list['train'] = train_dat['label'].tolist()

        src_list['valid'] = valid_dat['sentence1'].tolist()
        src_list['valid2'] = valid_dat['sentence2'].tolist()
        trg_list['valid'] = valid_dat['label'].tolist()

        src_list['test'] = test_dat['sentence1'].tolist()
        src_list['test2'] = test_dat['sentence2'].tolist()
        trg_list['test'] = test_dat['label'].tolist()

    if args.data_name == 'korean_hate_speech':
        args.data_path = os.path.join(args.data_path,'korean-hate-speech-detection')

        train_dat = pd.read_csv(os.path.join(args.data_path, 'train.hate.csv'))
        valid_dat = pd.read_csv(os.path.join(args.data_path, 'dev.hate.csv'))
        test_dat = pd.read_csv(os.path.join(args.data_path, 'test.hate.no_label.csv'))

        train_dat['label'] = train_dat['label'].replace('none', 0)
        train_dat['label'] = train_dat['label'].replace('hate', 1)
        train_dat['label'] = train_dat['label'].replace('offensive', 2)
        valid_dat['label'] = valid_dat['label'].replace('none', 0)
        valid_dat['label'] = valid_dat['label'].replace('hate', 1)
        valid_dat['label'] = valid_dat['label'].replace('offensive', 2)

        src_list['train'] = train_dat['comments'].tolist()
        src_list['train2'] = None
        trg_list['train'] = train_dat['label'].tolist()
        src_list['valid'] = valid_dat['comments'].tolist()
        src_list['valid2'] = None
        trg_list['valid'] = valid_dat['label'].tolist()
        src_list['test'] = test_dat['comments'].tolist()
        src_list['test2'] = None
        trg_list['test'] = [0 for _ in range(len(test_dat))]
        
    if args.data_name == 'rte':
        dataset = load_dataset("glue", args.data_name)
        train_dat = pd.DataFrame(dataset['train'])
        valid_dat = pd.DataFrame(dataset['validation'])
        test_dat = pd.DataFrame(dataset['test'])
        
        src_list['train'] = train_dat['sentence1'].tolist()
        src_list['train2'] = train_dat['sentence2'].tolist()
        trg_list['train'] = train_dat['label'].tolist()
        
        src_list['valid'] = valid_dat['sentence1'].tolist()
        src_list['valid2'] = valid_dat['sentence2'].tolist()
        trg_list['valid'] = valid_dat['label'].tolist()
        
        src_list['test'] = test_dat['sentence1'].tolist()
        src_list['test2'] = test_dat['sentence2'].tolist()
        trg_list['test'] = test_dat['label'].tolist()

    if args.data_name == 'gyafc':
        with open('/nas_homes/dataset/GYAFC_Corpus/Entertainment_Music/train/formal_em_train.txt', 'r') as f:
            formal_data = f.readlines()
        with open('/nas_homes/dataset/GYAFC_Corpus/Entertainment_Music/train/informal_em_train.txt', 'r') as f:
            informal_data = f.readlines()

        train_index, valid_index, test_index = data_split_index(formal_data, valid_ratio=args.valid_ratio, test_ratio=0)

        src_list['train'] = np.array(formal_data)[train_index]
        trg_list['train'] = np.array(informal_data)[train_index]

        src_list['valid'] = np.array(formal_data)[valid_index]
        trg_list['valid'] = np.array(informal_data)[valid_index]

        with open('/nas_homes/dataset/GYAFC_Corpus/Entertainment_Music/test/formal_em_test.txt', 'r') as f:
            formal_data = f.readlines()
        with open('/nas_homes/dataset/GYAFC_Corpus/Entertainment_Music/test/informal_em_test.txt', 'r') as f:
            informal_data = f.readlines()

        src_list['test'] = np.array(formal_data)
        trg_list['test'] = np.array(informal_data)

    return src_list, trg_list

def data_sampling(args, src_list, trg_list):

    data_len = len(src_list['train'])
    sample_num = int(data_len * args.sampling_ratio)

    sample_indx = np.random.choice(data_len, sample_num, replace=False)

    src_list['train'] = src_list['train'][sample_indx]
    trg_list['train'] = trg_list['train'][sample_indx]
    if src_list['train2'] != None:
        src_list['train2'] = src_list['train2'][sample_indx]

    return src_list, trg_list

def aug_data_load(args):

    aug_src_list = dict()
    aug_trg_list = list()

    if args.data_name == 'imdb':
        if args.aug_method == 'LLM':
            aug_dat = pd.read_csv('/home/kyohoon1/git_works/counterfactual/augmented/imdb/imdb_augmented_LLM_data.csv')
        if args.aug_method == 'ours':
            aug_dat = pd.read_csv('/home/kyohoon1/git_works/counterfactual/augmented/imdb/imdb_augmented_ours_data.csv')

        aug_src_list['train'] =  aug_dat['text'].tolist()
        aug_src_list['train2'] = None
        aug_trg_list = aug_dat['label'].tolist()

    if args.data_name == 'snli':
        if args.aug_method == 'LLM':
            aug_dat = pd.read_csv('/home/kyohoon1/git_works/counterfactual/augmented/snli/snli_augmented_LLM_data.csv')
        if args.aug_method == 'ours':
            aug_dat = pd.read_csv('/home/kyohoon1/git_works/counterfactual/augmented/snli/snli_augmented_ours_data.csv')

        a = aug_dat[aug_dat['label']=='entailment']
        b = aug_dat[aug_dat['label']=='contradiction']
        c = aug_dat[aug_dat['label']=='neutral']

        final_aug_dat = pd.concat([a,b,c], axis=0)

        aug_src_list['train'] = final_aug_dat['sent1'].tolist()
        aug_src_list['train2'] = final_aug_dat['sent2'].tolist()
        for label in final_aug_dat['label']:
            if label == 'entailment':
                aug_trg_list.append(0)
            if label == 'contradiction':
                aug_trg_list.append(1)
            if label == 'neutral':
                aug_trg_list.append(2)

    return aug_src_list, aug_trg_list

def tokenizing(args, src_list, tokenizer):
    processed_sequences = dict()
    processed_sequences['train'] = dict()
    processed_sequences['valid'] = dict()
    processed_sequences['test'] = dict()

    if args.data_name in ['mnli', 'mrpc']:
        for phase in ['train', 'valid', 'test']:
            encoded_dict = \
            tokenizer(
                src_list['f{phase}_sent1'], src_list['f{phase}_sent2'],
                max_length=args.src_max_len,
                padding='max_length',
                truncation=True
            )
            processed_sequences[phase]['input_ids'] = encoded_dict['input_ids']
            processed_sequences[phase]['attention_mask'] = encoded_dict['attention_mask']
            if args.encoder_model_type == 'bert':
                processed_sequences[phase]['token_type_ids'] = encoded_dict['token_type_ids']

    else:
        for phase in ['train', 'valid', 'test']:
            encoded_dict = \
            tokenizer(
                src_list[phase] if type(src_list[phase]) == list else src_list[phase].tolist(),
                max_length=args.src_max_len,
                padding='max_length',
                truncation=True
            )
            processed_sequences[phase]['input_ids'] = encoded_dict['input_ids']
            processed_sequences[phase]['attention_mask'] = encoded_dict['attention_mask']
            if args.encoder_model_type == 'bert':
                processed_sequences[phase]['token_type_ids'] = encoded_dict['token_type_ids']

    return processed_sequences

def input_to_device(batch_iter, device):

    src_sequence = batch_iter[0]
    src_att = batch_iter[1]
    src_seg = batch_iter[2]
    trg_label = batch_iter[3]

    src_sequence = src_sequence.to(device, non_blocking=True)
    src_att = src_att.to(device, non_blocking=True)
    src_seg = src_seg.to(device, non_blocking=True)
    trg_label = trg_label.type(torch.LongTensor)
    trg_label = trg_label.to(device, non_blocking=True)
    
    return src_sequence, src_att, src_seg, trg_label

def encoder_parameter_grad(model, on: bool = True):
    for para in model.encoder.parameters():
        para.requires_grad = on
    for para in model.latent_encoder.parameters():
        para.requires_grad = on
    for para in model.latent_decoder.parameters():
        para.requires_grad = on
    for para in model.classifier1.parameters():
        para.requires_grad = on
    for para in model.classifier1.parameters():
        para.requires_grad = on
    for para in model.classifier2.parameters():
        para.requires_grad = on
    for para in model.classifier3.parameters():
        para.requires_grad = on

    return model

def result_writing(args, task, accuracy, loss):
    fname = os.path.join(args.result_path, args.data_name, 'results.csv')
    
    # CSV file Making
    if not os.path.isfile(fname):
        result_dat = pd.DataFrame({
            'task': [],
            'seed': [],
            'sampling_ratio': [],
            'aug_encoder_model_type': [],
            'aug_decoder_model_type': [],
            'train_with_aug': [],
            'aug_method': [],
            'model_type': [],
            'test_decoding_strategy': [],
            'augmenting_label': [],
            'Accuracy': [],
            'Loss': []
        })
        result_dat.to_csv(fname, index=False)
    
    result_dat = pd.read_csv(fname)
    result = {
        'task': task,
        'seed': args.random_seed,
        'sampling_ratio': args.sampling_ratio,
        'train_with_aug': args.train_with_aug,
        'aug_method': args.aug_method,
        'model_type': args.model_type,
        'test_decoding_strategy': args.test_decoding_strategy,
        'augmenting_label': args.augmenting_label,
        'Accuracy': accuracy.item(),
        'Loss': loss.item()
    }
    result_dat = result_dat._append(result, ignore_index=True)
    result_dat.to_csv(fname, index=False)