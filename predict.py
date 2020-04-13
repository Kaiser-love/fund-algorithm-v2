from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import paddlehub as hub
from ViolateDataset import ViolateDataset


# if __name__ == '__main__':
def predict_tag(model_name, data):
    checkpoint_dir = "model/" + model_name
    dataset_dir = "data/" + model_name
    # Load Paddlehub ERNIE Tiny pretrained model
    module = hub.Module(name="ernie_tiny")
    inputs, outputs, program = module.context(
        trainable=UnicodeTranslateError, max_seq_len=128)
    # Download dataset and use accuracy as metrics
    # Choose dataset: GLUE/XNLI/ChinesesGLUE/NLPCC-DBQA/LCQMC
    dataset = ViolateDataset(dataset_dir=dataset_dir)
    # For ernie_tiny, it use sub-word to tokenize chinese sentence
    # If not ernie tiny, sp_model_path and word_dict_path should be set None
    reader = hub.reader.ClassifyReader(
        dataset=dataset,
        vocab_path=module.get_vocab_path(),
        max_seq_len=128,
        sp_model_path=module.get_spm_path(),
        word_dict_path=module.get_word_dict_path())

    # Construct transfer learning network
    # Use "pooled_output" for classification tasks on an entire sentence.
    # Use "sequence_output" for token-level output.
    pooled_output = outputs["pooled_output"]

    # Setup feed list for data feeder
    # Must feed all the tensor of module need
    feed_list = [
        inputs["input_ids"].name,
        inputs["position_ids"].name,
        inputs["segment_ids"].name,
        inputs["input_mask"].name,
    ]

    # Setup runing config for PaddleHub Finetune API
    config = hub.RunConfig(
        use_data_parallel=True,
        use_cuda=False,
        batch_size=24,
        checkpoint_dir=checkpoint_dir,
        strategy=hub.AdamWeightDecayStrategy())

    # Define a classfication finetune task by PaddleHub's API
    cls_task = hub.TextClassifierTask(
        data_reader=reader,
        feature=pooled_output,
        feed_list=feed_list,
        num_classes=dataset.num_labels,
        config=config)

    # Data to be prdicted
    # data = [["有保障"],
    #         ["无风险"],
    #         ["基金过往数据并不代表未来趋势"],
    #         ["为什么"],
    #         ["周杰伦"],
    #         ["吴东瀛"],
    #         ]
    # print(cls_task.predict(data=data, return_result=True))
    return cls_task.predict(data=data, return_result=True)
