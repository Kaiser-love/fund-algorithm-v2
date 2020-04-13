from paddlehub.dataset.base_nlp_dataset import BaseNLPDataset


class ViolateDataset(BaseNLPDataset):
    """DemoDataset"""

    def __init__(self, dataset_dir):
        # 数据集存放位置
        self.dataset_dir = dataset_dir
        super(ViolateDataset, self).__init__(
            base_path=self.dataset_dir,
            train_file="train.tsv",
            dev_file="dev.tsv",
            test_file="test.tsv",
            # 如果还有预测数据（不需要文本类别label），可以放在predict.tsv
            predict_file="predict.tsv",
            train_file_with_header=True,
            dev_file_with_header=True,
            test_file_with_header=True,
            predict_file_with_header=True,
            # 数据集类别集合
            label_list=["0", "1"])
