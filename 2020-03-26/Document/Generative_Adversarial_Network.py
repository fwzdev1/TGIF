#!/usr/bin/env python
# coding: utf-8

# In[24]:


import torch
import torchvision
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import torchvision.utils as vutils
import matplotlib.pyplot as plt
import numpy as np


dataroot = "c:\Datasets\celeba"
image_size = 64
print(29*"-"+"Data Loading......"+29*"-")
dataset = datasets.ImageFolder(root=dataroot,
                               transform=transforms.Compose([transforms.Resize(image_size),
                                                                transforms.CenterCrop(image_size),
                                                                transforms.ToTensor(),
                                                                transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5)),
                                                               ]))

dataloader = torch.utils.data.DataLoader(dataset, batch_size=128, shuffle=True, num_workers=2)
print(29*"-"+" Loading Finished "+29*"-")


# In[2]:


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# In[25]:


real_batch = next(iter(dataloader))
real_batch[0][0].size()
import time

plt.figure(figsize=(8, 8))
plt.axis("off")
plt.title("Faces of Celebrities")
# plt.imshow() displays images
# start = time.time()
# .to(device) speeds up imgs loading when the scale of imgs is large. On the contrary , it slows up.
plt.imshow(np.transpose(vutils.make_grid(real_batch[0].to(device)[:16], padding=2, normalize=True).cpu(), (1, 2, 0)))
# end = time.time()
# print("{:.6}s".format(end-start))


# In[4]:


import time

plt.figure(figsize=(8, 8))
plt.axis("off")
plt.title("Faces of Celebrities")
# plt.imshow() displays images
# start = time.time()
# .to(device) speeds up imgs loading when the scale of imgs is large. On the contrary , it slows up.
plt.imshow(np.transpose(vutils.make_grid(real_batch[0].to(device)[:16], padding=2, normalize=True).cpu(), (1, 2, 0)))
# end = time.time()
# print("{:.6}s".format(end-start))


# In[5]:


"""

SGD: mini_batch=128
initilization: all = a zero-centered Normal distribution with standard deviation 0.02
LeakyReLU: slope of leak=0.2
AdamOptimizer: lr=0.0002, belta1=0.5 helped stabilize training


"""

import torch
import torch.nn as nn
import torch.optim as optim # Optimizer
import torchvision
import torchvision.datasets as datasets
import torchvision.transforms as transforms # Data preprocessing
import torchvision.utils as vutils # Dataloader
import matplotlib.pyplot as plt
import numpy as np
import time


dataroot = "c:\Datasets\celeba"
image_size = 64
print(29*"-"+"Data Loading......"+29*"-")
dataset = datasets.ImageFolder(root=dataroot,
                               transform=transforms.Compose([transforms.Resize(image_size),
                                                                transforms.CenterCrop(image_size),
                                                                transforms.ToTensor(),
                                                                transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5)),]))

dataloader = torch.utils.data.DataLoader(dataset, batch_size=128, shuffle=True, num_workers=2)
print(29*"-"+" Loading Finished "+29*"-")
get_ipython().run_line_magic('matplotlib', 'inline')


# Size of feature maps in generator/discriminator
ngf = 64
ndf = 64
# Size of z latent vector(i.e. size of generator input)
nz = 100
# Number of channels in the training images. For color images this is 3
nc = 3
# Learning rate
lr =0.0002
# beta1 of parameters of AdamOptimizer
beta1 = 0.5
# Global Random Seed
GLOBAL_SEED = 1
def set_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    
# set_seed(GLOBAL_SEED)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
def weight_init(m):
    classname = m.__class__.__name__
    if classname.find("Conv") != -1:
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find("BatchNorm") != -1:
        nn.init.normal(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)
        
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.main = nn.Sequential(
            #100 x 1 x1 —— 512 x 4 x 4
            # nn.ConvTranspose2d(in_channel, out_channel, kernel_size, stride, padding)
            nn.ConvTranspose2d(nz, ngf*8, 4, 1, 0, bias=False),
            nn.BatchNorm2d(ngf*8),
            nn.ReLU(inplace=True),
            
            # 512 x 4 x 4 —— 256 x 8 x 8
            nn.ConvTranspose2d(ngf*8, ngf*4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf*4),
            nn.ReLU(inplace=True),
            
            # 256 x 8 x 8 —— 128 x 16 x 16
            nn.ConvTranspose2d(ngf*4, ngf*2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf*2),
            nn.ReLU(inplace=True),
            
            # 128 x 16 x 16 —— 64 x 32 x 32
            nn.ConvTranspose2d(ngf*2, ngf, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf),
            nn.ReLU(inplace=True),
            
            # 64 x 32 x 32 —— 3 x 64 x 64
            nn.ConvTranspose2d(ngf, nc, 4, 2, 1, bias=False),
            nn.Tanh()
        )
        
    def forward(self, input):
        return self.main(input)
                
class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.main = nn.Sequential(
            # nn.Conv2d(in_channel, out_channel, kernel_size, stride, padding)
            # 3 x 64 x 64 —— 64 x 32 x 32
            nn.Conv2d(nc, ndf, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, True),
            
            # 64 x 32 x 32 —— 128 x 16 x 16 
            nn.Conv2d(ndf, ndf*2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ndf*2),
            nn.LeakyReLU(0.2, True),
            
            # 128 x 16 x 16 —— 256 x 8 x 8
            nn.Conv2d(ndf*2, ndf*4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ndf*4),
            nn.LeakyReLU(0.2, True),

            # 256 x 8 x 8 —— 512 x 4 x 4
            nn.Conv2d(ndf*4, ndf*8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ndf*8),
            nn.LeakyReLU(0.2, True),

            # 512 x 4 x 4 —— 1 x 1 x 1
            nn.Conv2d(ndf*8, 1, 4, 1, 0, bias=False),
            nn.Sigmoid()
        )
        
    def forward(self, input):
        return self.main(input)

netG = Generator().to(device)

netG.apply(weight_init)

netD = Discriminator().to(device)

netD.apply(weight_init)
# Binary Cross-Entropy Loss Function
criterion = nn.BCELoss()

# real/fake labels
real_label = 1
fake_label = 0

iters = 0


fixed_noise = torch.randn(64, nz, 1, 1, device=device)
    
# Optimizer of Generator n Discriminator
optimizerD = optim.Adam(netD.parameters(), lr=lr, betas=(beta1, 0.999))
optimizerG = optim.Adam(netG.parameters(), lr=lr, betas=(beta1, 0.999))

# Training epochs
epochs = 5

# Training
G_losses = []
D_losses = []
print(29*"-"+"Start Training Loop..."+29*"-")
time_start = time.time()
for epoch in range(epochs):
    # data: a list of [num_batch_data, channels, height, width]
    for i, data in enumerate(dataloader, 0):
        # Firstly, training Discriminator with real data : maximize log(D(x)) + log(1-D(G(z)))
        netD.zero_grad()
        real_data = data[0].to(device)
        # Number of real data(s) of each batches
        data_size = real_data.size(0)
        # Real labels
        label = torch.full((data_size,), real_label, device=device)
        output = netD(real_data).view(-1)
        errD_real = criterion(output, label)
        errD_real.backward()
#         optimizerD.step()
        D_x = output.mean().item()
        
        # Then traning Discriminator with fake data
        # Fake data generation
        random_noise = torch.randn(data_size, nz, 1, 1, device=device)
        # 128 x 100 x 1 x 1 —— 128 x 3 x 64 x 64
        fake_input = netG(random_noise)
        label.fill_(fake_label)
        # fix Generator n train Discriminator
        fake_output = netD(fake_input.detach()).view(-1)
        errD_fake = criterion(fake_output, label)
        errD_fake.backward()
        D_G_z1 = fake_output.mean().item()
        errD = errD_real + errD_fake
        optimizerD.step()
        
        #Training Generator : maximize log(D(G(z)))
        netG.zero_grad()
        label.fill_(real_label)
        output = netD(fake_input).view(-1)
        errG = criterion(output, label)
        errG.backward()
        D_G_z2 = output.mean().item()
        optimizerG.step()
        
        
        # Training stats
        if i%50 == 0:
            print(74*"-")
            print("[{}/{}][{}/{}] | Loss D: {:.3f} | Loss G: {:.3f} | D(x): {:.3f} | D(G(z)): {:.3f}/{:.3f}"
                  .format(epoch, epochs, i, len(dataloader), errD.item(), errG.item(), D_x, D_G_z1, D_G_z2))
        G_losses.append(errG.item())
        D_losses.append(errD.item())
        
        iters += 1
        
    out_img = netG(fixed_noise).detach().cpu()
    img_list = []
    img_list.append(vutils.make_grid(out_img, padding=3, normalize=True))

    plt.figure(figsize=(15,15))
    plt.axis("off")
    plt.title("Generated Images")
    plt.imshow(np.transpose(img_list[-1], (1, 2, 0)))
    plt.show()
print(29*"-"+"Game Finished"+29*"-")
time_end = time.time()
print("Time consumption: {:.3f}mins".format((time_end-time_start)/60))
# state = {'G':netG.state_dict(), 'D':netD.state_dict(), 'oG':optimizerG.state_dict(),'oD':optimizerD.state_dict(),  'epoch':epochs}
# PATH = './DCGAN_Generative_Adversarial_Network_celeb.pth'
# torch.save(state, PATH)


# In[ ]:





# In[7]:


state = {'G':netG.state_dict(), 'D':netD.state_dict(), 'oG':optimizerG.state_dict(),'oD':optimizerD.state_dict(),  'epoch':epochs}
PATH = './DCGAN_Generative_Adversarial_Network_celeb.pth'
torch.save(state, PATH)


# In[ ]:


# Continue training
checkpoint = torch.load(PATH)
netG.load_state_dict(checkpoint['G'])
netD.load_state_dict(checkpoint['D'])
optimizerG.load_state_dict(checkpoint['oG'])
optimizerD.load_state_dict(checkpoint['oD'])

epochs = 20
for epoch in range(epochs):
    for i, data in enumerate(dataloader, 0):
        netD.zero_grad()
        # real
        real_data = data[0].to(device)
        data_size = real_data.size(0)
        label = torch.full((data_size,), 1, device=device)
        


# In[ ]:


# Continue training
checkpoint = torch.load(PATH)
netG.load_state_dict(checkpoint['G'])
netD.load_state_dict(checkpoint['D'])
optimizerG.load_state_dict(checkpoint['oG'])
optimizerD.load_state_dict(checkpoint['oD'])

criterion = nn.BCELoss()

# real/fake labels
real_label = 1
fake_label = 0

fixed_noise = torch.randn(30, nz, 1, 1, device=device)
    
# Optimizer of Generator n Discriminator
# optimizerD = optim.Adam(netD.parameters(), lr=lr, betas=(beta1, 0.999))
# optimizerG = optim.Adam(netG.parameters(), lr=lr, betas=(beta1, 0.999))

# Training epochs
epochs = 20

print(29*"-"+"Start Training Loop..."+29*"-")
time_start = time.time()
for epoch in range(epochs):
    # data: a list of [num_batch_data, channels, height, width]
    for i, data in enumerate(dataloader, 0):
        # Firstly, training Discriminator with real data : maximize log(D(x)) + log(1-D(G(z)))
        netD.zero_grad()
        real_data = data[0].to(device)
        # Number of real data(s) of each batches
        data_size = real_data.size(0)
        # Real labels
        label = torch.full((data_size,), real_label, device=device)
        output = netD(real_data).view(-1)
        errD_real = criterion(output, label)
        errD_real.backward()
#         optimizerD.step()
        D_x = output.mean().item()
        
        # Then traning Discriminator with fake data
        # Fake data generation
        random_noise = torch.randn(data_size, nz, 1, 1, device=device)
        # 128 x 100 x 1 x 1 —— 128 x 3 x 64 x 64
        fake_input = netG(random_noise)
        label.fill_(fake_label)
        # fix Generator n train Discriminator
        fake_output = netD(fake_input.detach()).view(-1)
        errD_fake = criterion(fake_output, label)
        errD_fake.backward()
        D_G_z1 = fake_output.mean().item()
        errD = errD_real + errD_fake
        optimizerD.step()
        
        #Training Generator : maximize log(D(G(z)))
        netG.zero_grad()
        label.fill_(real_label)
        output = netD(fake_input).view(-1)
        errG = criterion(output, label)
        errG.backward()
        D_G_z2 = output.mean().item()
        optimizerG.step()
        
        
        # Training stats
        if i%50 == 0:
            print(74*"-")
            print("[{}/{}][{}/{}] | Loss D: {:.3f} | Loss G: {:.3f} | D(x): {:.3f} | D(G(z)): {:.3f}/{:.3f}"
                  .format(epoch, epochs, i, len(dataloader), errD.item(), errG.item(), D_x, D_G_z1, D_G_z2))
        G_losses.append(errG.item())
        D_losses.append(errD.item())
        
        iters += 1
        
    out_img = netG(fixed_noise).detach().cpu()
    img_list = []
    img_list.append(vutils.make_grid(out_img, padding=3, normalize=True))

    plt.figure(figsize=(15,15))
    plt.axis("off")
    plt.title("Generated Images")
    plt.imshow(np.transpose(img_list[-1], (1, 2, 0)))
    plt.show()
print(29*"-"+"Game Finished"+29*"-")
time_end = time.time()
print("Time consumption: {:.3f}mins".format((time_end-time_start)/60))
state = {'G':netG.state_dict(), 'D':netD.state_dict(), 'oG':optimizerG.state_dict(),'oD':optimizerD.state_dict(),  'epoch':epochs}
PATH = './DCGAN_Generative_Adversarial_Network_celeb.pth'
torch.save(state, PATH)


# In[35]:


# Model loading
PATH = 'c:\Datasets\celeba'
checkpoint = torch.load(PATH)
netG.load_state_dict(checkpoint['G'])
print("Model loaded")

fixed_noise = torch.randn(30, nz, 1, 1, device=device)

def display(img):
    img = vutils.make_grid(out_img, padding=3, normalize=True)
    print(29*"-"+"Feature Maps displayed"+29*"-")
    plt.figure(figsize=(15,15))
    plt.axis("off")
    plt.title("Feature Map")
    plt.imshow(np.transpose(img, (1, 2, 0)))
    plt.show()
    
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.conv1 = nn.ConvTranspose2d(nz, ngf*8, 4, 1, 0, bias=False),
        self.bn1 = nn.BatchNorm2d(ngf*8),
        self.relu = nn.ReLU(inplace=True),

        # 512 x 4 x 4 —— 256 x 8 x 8
        self.conv2 = nn.ConvTranspose2d(ngf*8, ngf*4, 4, 2, 1, bias=False),
        sel.bn2 = nn.BatchNorm2d(ngf*4),
#         nn.ReLU(inplace=True),

        # 256 x 8 x 8 —— 128 x 16 x 16
        self.conv3 = nn.ConvTranspose2d(ngf*4, ngf*2, 4, 2, 1, bias=False),
        self.bn3 = nn.BatchNorm2d(ngf*2),
#         nn.ReLU(inplace=True),

        # 128 x 16 x 16 —— 64 x 32 x 32
        self.conv4 = nn.ConvTranspose2d(ngf*2, ngf, 4, 2, 1, bias=False),
        self.bn4 = nn.BatchNorm2d(ngf),
#         nn.ReLU(inplace=True),

        # 64 x 32 x 32 —— 3 x 64 x 64
        self.conv5 = nn.ConvTranspose2d(ngf, nc, 4, 2, 1, bias=False),
        self.tanh = nn.Tanh()
        
    def forward(self, x):
        x = self.conv1(x)
        display(x)
        x = self.bn1(x)
        x = self.relu(x)
        
        x = self.conv2(x)
        display(x)
        x = self.bn2(x)
        x = self.relu(x)
        
        x = self.conv3(x)
        display(x)
        x = self.bn3(x)
        x = self.relu(x)
        
        x = self.conv4(x)
        display(x)
        x = self.bn4(x)
        x = self.relu(x)
        
        x = self.conv5(x)
        display(x)
        x = self.tanh(x)
        return x

out_img = netG(fixed_noise).detach().cpu()


# In[ ]:




