import torch
import torch.nn as nn
import torch.functional as F

class UNet(nn.Module):
    def __init__(self, input_nc, output_nc):
        super(UNet, self).__init__()
        self.in_conv1 = nn.Sequential(
            nn.Conv2d(input_nc, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.Tanh()
        )
        
        self.in_conv2 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.Tanh()
        )
        self.pooling1 = nn.MaxPool2d(2)
        self.conv1_1 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.Tanh()
        )
        self.conv1_2 = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
             nn.Tanh()
        )
        self.pooling2 = nn.MaxPool2d(2)
        self.conv2_1 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.Tanh()
        )
        self.conv2_2 = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.Tanh()
        )

        self.pooling3 = nn.MaxPool2d(2)
        self.conv3_1 = nn.Sequential(
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.Tanh()
        )
        self.conv3_2 = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.Tanh()
        )

        self.pooling4 = nn.MaxPool2d(2)
        self.conv4_1 = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.Tanh()
        )
        self.conv4_2 = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.Tanh()
        )

        self.upsampling1 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.conv5_1 = nn.Sequential(
            nn.Conv2d(1024, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.Tanh()
        )
        self.conv5_2 = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.Tanh()
        )

        self.upsampling2 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.conv6_1 = nn.Sequential(
            nn.Conv2d(512, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.Tanh()
        )

        self.conv6_2 = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.Tanh()
        )

        self.upsampling3 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.conv7_1 = nn.Sequential(
            nn.Conv2d(256, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.Tanh()
        )
        self.conv7_2 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.Tanh()
        )

        self.upsampling4 = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.conv8_1 = nn.Sequential(
            nn.Conv2d(128, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.Tanh()
        )
        self.conv8_2 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.Tanh()
        )

        self.out_conv = nn.Sequential(
            nn.Conv2d(64, 32, 1, bias=False),
            nn.Tanh(),
            nn.Conv2d(32, 16, 1, bias=False),
            nn.Tanh(),
            nn.Conv2d(16, 1, 1, bias=False)
        )
        
        # nn.Conv2d(64, output_nc, kernel_size=1, stride=1, padding=0)

        # self.bn64 = nn.BatchNorm2d(64)
        # self.bn128 = nn.BatchNorm2d(128)
        # self.bn256 = nn.BatchNorm2d(256)
        # self.bn512 = nn.BatchNorm2d(512)
        self.bn64 = nn.Sequential()
        self.bn128 = nn.Sequential()
        self.bn256 = nn.Sequential()
        self.bn512 = nn.Sequential()

        # self.relu = nn.ReLU(inplace=True)
        self.relu = nn.Sequential()
        self.sigmoid = nn.Sigmoid()
        self.apply(self._init_weights)
        
    def _init_weights(self, m: nn.Module):
        """
        out_proj.weight which is previously initilized in VSSBlock, would be cleared in nn.Linear
        no fc.weight found in the any of the model parameters
        no nn.Embedding found in the any of the model parameters
        so the thing is, VSSBlock initialization is useless
        
        Conv2D is not intialized !!!
        """
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)
        
    def forward(self, input):
        # input = input / input.max()
        # print('input', input.max(), input.min())
        c1 = self.relu(self.bn64(self.in_conv1(input)))
        c2 = self.relu(self.bn64(self.in_conv2(c1)))

        e1_ = self.relu(self.bn128(self.conv1_1(self.pooling1(c2))))
        e1 = self.relu(self.bn128(self.conv1_2(e1_)))

        e2_ = self.relu(self.bn256(self.conv2_1(self.pooling1(e1))))
        e2 = self.relu(self.bn256(self.conv2_2(e2_)))

        e3_ = self.relu(self.bn512(self.conv3_1(self.pooling1(e2))))
        e3 = self.relu(self.bn512(self.conv3_2(e3_)))

        e4_ = self.relu(self.bn512(self.conv4_1(self.pooling1(e3))))
        e4 = self.relu(self.bn512(self.conv4_2(e4_)))

        d1_1 = self.upsampling1(e4)
        d1_2 = torch.cat([d1_1, e3], dim=1)
        d1_ = self.relu(self.bn256(self.conv5_1(d1_2)))
        d1 = self.relu(self.bn256(self.conv5_2(d1_)))

        d2_1 = self.upsampling1(d1)
        d2_2 = torch.cat([d2_1, e2], dim=1)
        d2_ = self.relu(self.bn128(self.conv6_1(d2_2)))
        d2 = self.relu(self.bn128(self.conv6_2(d2_)))

        d3_1 = self.upsampling1(d2)
        d3_2 = torch.cat([d3_1, e1], dim=1)
        d3_ = self.relu(self.bn64(self.conv7_1(d3_2)))
        d3 = self.relu(self.bn64(self.conv7_2(d3_)))

        d4_1 = self.upsampling1(d3)
        d4_2 = torch.cat([d4_1, c2], dim=1)
        d4_ = self.relu(self.bn64(self.conv8_1(d4_2)))
        d4 = self.relu(self.bn64(self.conv8_2(d4_)))
        # print('d4', d4.max(), d4.min())
        # print(d4.size()) torch.Size([1, 64, 256, 256])
        output = self.out_conv(d4)
        print('output', output.max(), output.min())
        # print(output.mean())
        return output

if __name__=="__main__":
    model = UNet(3, 1)

    # (B,C,H,W)
    input=torch.randn(1,3,256,256)

    print(model.forward(input).size())

    print(model.__class__.__name__)