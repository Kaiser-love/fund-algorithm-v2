import paddlehub as hub

from ViolateDataset import ViolateDataset
import os


def is_path_valid(path):
    if path == "":
        return False
    path = os.path.abspath(path)
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return True


# tensorboard --logdir visualization
# if __name__ == '__main__':
def train_model(model_name):
    checkpoint_dir = "model/" + model_name
    dataset_dir = "data/" + model_name
    # Load Paddlehub ERNIE Tiny pretrained model
    module = hub.Module(name="ernie_tiny")
    inputs, outputs, program = module.context(
        trainable=True, max_seq_len=128)

    # Download dataset and use accuracy as metrics
    # Choose dataset: GLUE/XNLI/ChinesesGLUE/NLPCC-DBQA/LCQMC
    # metric should be acc, f1 or matthews
    # dataset = hub.dataset.ChnSentiCorp()
    dataset = ViolateDataset(dataset_dir=dataset_dir)
    metrics_choices = ["acc"]

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

    # Select finetune strategy, setup config and finetune
    strategy = hub.AdamWeightDecayStrategy(
        warmup_proportion=0.1,
        weight_decay=0.01,
        learning_rate=5e-5,
        lr_scheduler="linear_decay")

    # Setup runing config for PaddleHub Finetune API
    config = hub.RunConfig(
        use_data_parallel=True,
        use_cuda=False,
        num_epoch=3,
        batch_size=24,
        checkpoint_dir=checkpoint_dir,
        # model_dir="./models",
        enable_memory_optim=True,
        strategy=strategy)

    # Define a classfication finetune task by PaddleHub's API
    cls_task = hub.TextClassifierTask(
        data_reader=reader,
        feature=pooled_output,
        feed_list=feed_list,
        num_classes=dataset.num_labels,
        config=config,
        metrics_choices=metrics_choices)
    # with cls_task.phase_guard(phase="train"):
    #     cls_task.init_if_necessary()
    #     cls_task.load_parameters("./models/model")
    # Finetune and evaluate by PaddleHub's API
    # will finish training, evaluation, testing, save model automatically
    # cls_task.finetune_and_eval()
    cls_task.finetune()
    # Evaluate by PaddleHub's API
    run_states = cls_task.eval()
    # Get acc score on dev
    eval_avg_score, eval_avg_loss, eval_run_speed = cls_task._calculate_metrics(
        run_states)
    # acc on dev will be used by auto finetune
    print("AutoFinetuneEval" + "\t" + str(float(eval_avg_score["acc"])))
