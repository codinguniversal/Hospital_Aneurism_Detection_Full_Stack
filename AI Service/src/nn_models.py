import numpy as np
import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence
from torchvision.models import resnet50, squeezenet1_1, SqueezeNet1_1_Weights
from huggingface_hub import hf_hub_download
from torch.amp import autocast
import timm
from timm.models._manipulate import adapt_input_conv

def apply_threshold_scale_cta(slice2d, new_min, new_max):
    '''
    MIN_CT / MAX_CT comes from load_dicom_series
    '''
    MIN_CT = -1024
    MAX_CT = 3071
    slice2d = slice2d * (MAX_CT - MIN_CT) + MIN_CT
    slice2d = np.clip(slice2d, new_min, new_max)
    slice2d = (slice2d - new_min) / (new_max - new_min)
    return slice2d

def apply_transform_1d(x, modality):
    '''
    Function to clip CTA between new_min and new_max
    '''
    # x is of dim [z, x, y]
    x_shape = x.shape
    slice_2d_seq = []
    for i in range(0, x_shape[0]):
        with torch.no_grad():
            slice_2d = x[i, :, :]  # [batch, x, y]
            if modality:
                slice_2d = apply_threshold_scale_cta(
                    slice_2d, -100, 600
                )  # [ C=1, x, y]
            slice_2d_seq.append(slice_2d)
    return slice_2d_seq

class Cnn2dAdapter25(nn.Module):
    '''
    The following network shape idea has been taken from
    https://www.kaggle.com/code/yosukeyama/rsna2025-32ch-img-infer-lb-0-69-share

    '''
    def __init__(self, input_channels, num_classes=14):
        super().__init__()
        self.input_channels = input_channels
        self.num_classes = num_classes

        self.backbone = timm.create_model(
                "tf_efficientnetv2_s.in21k_ft_in1k", 
                num_classes=self.num_classes, 
                pretrained=True,
                drop_rate=0.5,
                in_chans=self.input_channels
            )

        for param in self.backbone.parameters():
            param.requires_grad = True

    def forward(self, x, lengths = []):
        x = x.permute(1, 2, 0, 3,4).squeeze(1)
        x = self.backbone(x)
        return x

class Cnn2dAdapter12(nn.Module):
    '''
    The two following models (Cnn2dAdapter12 and Cnn2dAdapter13) have been trained using the weights of
    https://huggingface.co/Lab-Rasool/RadImageNet
    https://github.com/BMEII-AI/RadImageNet
    @article{doi:10.1148/ryai.210315,
    author = {Mei, Xueyan and Liu, Zelong and Robson, Philip M. and Marinelli, Brett and Huang, Mingqian and Doshi, Amish and Jacobi, Adam and Cao, Chendi and Link, Katherine E. and Yang, Thomas and Wang, Ying and Greenspan, Hayit and Deyer, Timothy and Fayad, Zahi A. and Yang, Yang},
    title = {RadImageNet: An Open Radiologic Deep Learning Research Dataset for Effective Transfer Learning}}
    '''
    def __init__(self, input_channels, num_classes=13):
        super().__init__()
        self.input_channels = input_channels
        self.num_classes = num_classes

        model_path = hf_hub_download(
            repo_id="Lab-Rasool/RadImageNet", filename="ResNet50.pt"
        )
        state_dict = torch.load(
            model_path, map_location="cuda" if torch.cuda.is_available() else "cpu"
        )

        self.backbone = timm.create_model(
            "resnet50",
            num_classes=self.num_classes,
            pretrained=False,
            drop_rate=0.3,
            in_chans=self.input_channels,
            drop_path_rate=0.2,
        )

        keys0 = list(state_dict.keys())
        keys1 = list(self.backbone.state_dict().keys())

        for i in range(0, len(keys0)):
            #weights0 = state_dict[keys0[i]]
            #weights1 = self.backbone.state_dict()[keys1[i]]
            # print(f"{keys0[i]:60} {keys1[i]:60} {str(weights0.size() == weights1.size()):10}")
            state_dict[keys1[i]] = state_dict.pop(keys0[i])

        state_dict["conv1.weight"] = adapt_input_conv(
            in_chans=self.input_channels, conv_weight=state_dict["conv1.weight"]
        )

        missing, unexpected = self.backbone.load_state_dict(state_dict, strict=False)
        print("Missing keys:", missing)
        print("Unexpected keys:", unexpected)

        for param in self.backbone.parameters():
            param.requires_grad = True

    def forward(self, x, l=[]):
        x = x.permute(1, 2, 0, 3, 4).squeeze(1)
        x = self.backbone(x)
        return x


class Cnn2dAdapter13(Cnn2dAdapter12):
    def __init__(self, input_channels, num_classes=14):
        super().__init__(input_channels=input_channels, num_classes=num_classes)


#class Cnn3dAdapter(nn.Module):
#   '''
#    You need to run pip install timm-3d for this one
#    https://github.com/ZFTurbo/timm_3d
#    @article{solovyev20223d,
#    title={3D convolutional neural networks for stalled brain capillary detection},
#    author={Solovyev, Roman and Kalinin, Alexandr A and Gabruseva, Tatiana},
#   '''
#   def __init__(self, input_channels, num_classes=13):
#       super().__init__()
#       self.input_channels = input_channels
#       self.num_classes = num_classes
#       self.backbone = timm_3d.create_model(
#               "tf_efficientnetv2_s.in21k_ft_in1k",
#               num_classes=self.num_classes,
#               pretrained=True,
#               drop_rate=0.3,
#               drop_path_rate=0.2
#           )
#       for param in self.backbone.parameters():
#           param.requires_grad = True
#   def forward(self, x, l = []):
#       # depth, batch, channel , width, height
#       x = x.permute(1, 2, 3, 4, 0) #(B, C, H, W, D)
#       x = self.backbone(x)
#       return x


class LSTMCNN(nn.Module):
    """
    --------------------------------  Ht -------------------------
    --------------------------------  |  -------------------------
    -- slice_2d_t --> CNN --> Xt --> LSTM --> Yt = has_aneurysm --
    --------------------------------------------------------------
    """

    def __init__(
        self: nn.Module,
        device,
        input_size=128,  # 256
        hidden_size=64,
        num_layers=1,  # 1
        num_class=14,
    ):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_class = num_class
        self.device = device

        self.cnn = squeezenet1_1(SqueezeNet1_1_Weights.IMAGENET1K_V1)
        self.cnn.classifier[1] = nn.Conv2d(512, input_size, kernel_size=1)

        for param in self.cnn.parameters():
            param.requires_grad = True

        self.lstm = nn.LSTM(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            batch_first=False,
            dropout=0.3,
            bidirectional=True,
        )

        self.linear = nn.Linear(self.hidden_size * 2, self.num_class)
        self.norm = nn.LayerNorm(self.hidden_size * 2)

    def cnn_encode(self, x):
        # x is of size [D, B, C=3, x, y]
        x_encoded_seq = []
        for i in range(0, x.shape[0]):
            encode = self.cnn(x[i].contiguous())
            with torch.no_grad():
                x_encoded_seq.append(encode)
        return torch.stack(x_encoded_seq)  # [seq len = z, batch, input_size]

    def forward(self, x, lengths):
        # x is of size [D, B, C, x, y]
        with autocast(device_type="cuda"):
            x_encoded_seq = self.cnn_encode(x)

            packed = pack_padded_sequence(
                x_encoded_seq, lengths.cpu(), enforce_sorted=False
            )
            out, (ht, ct) = self.lstm(packed)
            htn = self.norm(torch.cat((ht[-2, :, :], ht[-1, :, :]), dim=1))
            y = self.linear(htn)
        return y
    
class WinAll(nn.Module):
    '''
    ------------------------------------------ ----------------------------------------
    -----------------------------------------------------------------------------------
    -- Slices --> RadImageNet resnet50 --> Encoded Slices --> MLP --> Yt = has_aneurysm
    -----------------------------------------------------------------------------------

    The following models uses
    https://huggingface.co/Lab-Rasool/RadImageNet
    https://github.com/BMEII-AI/RadImageNet
    @article{doi:10.1148/ryai.210315,
    author = {Mei, Xueyan and Liu, Zelong and Robson, Philip M. and Marinelli, Brett and Huang, Mingqian and Doshi, Amish and Jacobi, Adam and Cao, Chendi and Link, Katherine E. and Yang, Thomas and Wang, Ying and Greenspan, Hayit and Deyer, Timothy and Fayad, Zahi A. and Yang, Yang},
    title = {RadImageNet: An Open Radiologic Deep Learning Research Dataset for Effective Transfer Learning}}
    '''
    def __init__(self, depth_size, num_classes=14):
        super().__init__()
        self.depth_size = depth_size
        self.num_classes = num_classes

        model_path = hf_hub_download(
            repo_id="Lab-Rasool/RadImageNet", filename="ResNet50.pt"
        )
        state_dict = torch.load(
            model_path, map_location="cuda" if torch.cuda.is_available() else "cpu"
        )

        self.backbone = timm.create_model(
            "resnet50",
            num_classes=0,
            pretrained=False,
            drop_rate=0.3,
            drop_path_rate=0.1,
            in_chans=3,
        )

        keys0 = list(state_dict.keys())
        keys1 = list(self.backbone.state_dict().keys())

        for i in range(0, len(keys0)):
            state_dict[keys1[i]] = state_dict.pop(keys0[i])

        missing, unexpected = self.backbone.load_state_dict(state_dict, strict=False)
        print("Missing keys:", missing)
        print("Unexpected keys:", unexpected)

        self.classifier = nn.Sequential(
            nn.Dropout(0.1),
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 64),
            nn.ReLU(),
        )

        self.final_layer = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(self.depth_size * 64, self.depth_size * 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(self.depth_size * 32, self.depth_size * 16),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(self.depth_size * 16, self.num_classes),
        )

    def forward(self, x, l=[]):
        # depth, batch, channel , width, height
        x = x.permute(1, 0, 2, 3, 4)  # batch, depth , channel , width, height
        y_list = []
        for i in range(0, x.shape[0]):
            # input (depth , channel , width, height) output  (depth , 2048)
            image_features = self.backbone(x[i])
            encoded_features = self.classifier(image_features)  # output (depth , 32)
            encoded_features = torch.flatten(encoded_features)
            encoded_features = self.final_layer(encoded_features)
            y_list.append(encoded_features)
        y = torch.stack(y_list, 0)
        return y



