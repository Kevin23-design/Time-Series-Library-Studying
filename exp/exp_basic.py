import os
import torch
import importlib
import pkgutil  
import csv

import numpy as np
import matplotlib.pyplot as plt

plt.switch_backend('agg')

# Just put your model files under models/ folder
# e.g., models/Transformer.py, models/LSTM.py, etc.
# All models will be automatically detected and can be used by specifying their names.

class Exp_Basic(object):
    def __init__(self, args):
        self.args = args
        
        # -------------------------------------------------------
        #  Automatically generate model map
        # -------------------------------------------------------
        model_map = self._scan_models_directory()

        # Use smart dictionary
        self.model_dict = LazyModelDict(model_map)

        self.device = self._acquire_device()
        self.model = self._build_model().to(self.device)
        self.training_history = []
        self.training_history_columns = []

    def reset_training_history(self):
        self.training_history = []
        self.training_history_columns = []

    def _to_scalar(self, value):
        if value is None:
            return np.nan
        if isinstance(value, (int, float, np.floating)):
            return float(value)
        if torch.is_tensor(value):
            return float(value.detach().cpu().item())
        return float(value)

    def record_training_history(self, epoch, train_loss, vali_loss, test_loss, extra_metrics=None):
        record = {
            'epoch': int(epoch),
            'train_loss': self._to_scalar(train_loss),
            'vali_loss': self._to_scalar(vali_loss),
            'test_loss': self._to_scalar(test_loss),
        }
        if extra_metrics:
            for key, value in extra_metrics.items():
                record[key] = self._to_scalar(value)
        self.training_history.append(record)

    def save_training_history(self, save_dir):
        if not self.training_history:
            return None

        columns = ['epoch', 'train_loss', 'vali_loss', 'test_loss']
        extra_columns = {
            key for record in self.training_history for key in record.keys()
            if key not in columns
        }

        # Keep common accuracy columns ordered for stable plotting.
        for key in ['vali_acc', 'test_acc']:
            if key in extra_columns:
                columns.append(key)
                extra_columns.remove(key)
        columns.extend(sorted(extra_columns))
        self.training_history_columns = columns

        history_array = np.array([
            [record.get(column, np.nan) for column in columns]
            for record in self.training_history
        ], dtype=np.float64)

        os.makedirs(save_dir, exist_ok=True)

        npy_path = os.path.join(save_dir, 'training_history.npy')
        np.save(npy_path, history_array)

        csv_path = os.path.join(save_dir, 'training_history.csv')
        with open(csv_path, 'w', newline='') as fp:
            writer = csv.writer(fp)
            writer.writerow(columns)
            writer.writerows(history_array.tolist())

        return history_array

    def plot_training_curve(self, save_dir, history_array=None):
        if history_array is None:
            history_array = self.save_training_history(save_dir)
        if history_array is None or history_array.size == 0:
            return

        columns = self.training_history_columns or ['epoch', 'train_loss', 'vali_loss', 'test_loss']
        idx = {name: i for i, name in enumerate(columns)}

        epochs = history_array[:, idx['epoch']]
        train_loss = history_array[:, idx['train_loss']]
        vali_loss = history_array[:, idx['vali_loss']]
        test_loss = history_array[:, idx['test_loss']]

        fig, ax1 = plt.subplots(figsize=(8, 5))
        ax1.plot(epochs, train_loss, label='Train Loss', linewidth=2)
        ax1.plot(epochs, vali_loss, label='Vali Loss', linewidth=2)
        ax1.plot(epochs, test_loss, label='Test Loss', linewidth=2)
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.grid(alpha=0.3)

        if 'vali_acc' in idx and 'test_acc' in idx:
            ax2 = ax1.twinx()
            vali_acc = history_array[:, idx['vali_acc']]
            test_acc = history_array[:, idx['test_acc']]
            ax2.plot(epochs, vali_acc, label='Vali Acc', linestyle='--', linewidth=1.8, color='tab:green')
            ax2.plot(epochs, test_acc, label='Test Acc', linestyle='--', linewidth=1.8, color='tab:red')
            ax2.set_ylabel('Accuracy')

            lines_1, labels_1 = ax1.get_legend_handles_labels()
            lines_2, labels_2 = ax2.get_legend_handles_labels()
            ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='best')
        else:
            ax1.legend(loc='best')

        fig.tight_layout()
        fig.savefig(os.path.join(save_dir, 'training_curve.png'), bbox_inches='tight')
        plt.close(fig)

    def _scan_models_directory(self):
        """
        Automatically scan all .py files in the models folder
        """
        model_map = {}
        models_dir = 'models'

        # Iterate through all files in 'models' directory
        if os.path.exists(models_dir):
            for filename in os.listdir(models_dir):
                # Ignore __init__.py and non-.py files
                if filename.endswith('.py') and filename != '__init__.py':
                    # Remove .py extension to get module name
                    module_name = filename[:-3]
                    
                    # Build full import path
                    full_path = f"{models_dir}.{module_name}"
                    
                    # loading dict: {'Transformer': 'models.Transformer'}
                    model_map[module_name] = full_path
        
        return model_map

    def _build_model(self):
        raise NotImplementedError
        return None

    def _acquire_device(self):
        if self.args.use_gpu and self.args.gpu_type == 'cuda':
            os.environ["CUDA_VISIBLE_DEVICES"] = str(
                self.args.gpu) if not self.args.use_multi_gpu else self.args.devices
            device = torch.device('cuda:{}'.format(self.args.gpu))
            print('Use GPU: cuda:{}'.format(self.args.gpu))
        elif self.args.use_gpu and self.args.gpu_type == 'mps':
            device = torch.device('mps')
            print('Use GPU: mps')
        else:
            device = torch.device('cpu')
            print('Use CPU')
        return device

    def _get_data(self):
        pass

    def vali(self):
        pass

    def train(self):
        pass

    def test(self):
        pass


class LazyModelDict(dict):
    """
    Smart Lazy-Loading Dictionary
    """
    def __init__(self, model_map):
        self.model_map = model_map
        super().__init__()

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        
        if key not in self.model_map:
            raise NotImplementedError(f"Model [{key}] not found in 'models' directory.")
            
        module_path = self.model_map[key]
        try:
            print(f"🚀 Lazy Loading: {key} ...") 
            module = importlib.import_module(module_path)
        except ImportError as e:
            print(f"❌ Error: Failed to import model [{key}]. Dependencies missing?")
            raise e

        # Try to find the model class
        if hasattr(module, 'Model'):
            model_class = module.Model
        elif hasattr(module, key):
            model_class = getattr(module, key)
        else:
            raise AttributeError(f"Module {module_path} has no class 'Model' or '{key}'")

        self[key] = model_class
        return model_class

