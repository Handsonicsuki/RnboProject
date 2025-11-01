# Setting up a development environment
This document discusses how to setup a development environment for building SSP modules.


# General workflow
There are three steps to build SSP modules, which must be completed in order.

a) setup the development environment 
done once, and overed in DEVENV.md

b) download/create project 
done once, per project, and covered in this document.

c) build project
done each time you want to build/create the modules for the SSP


note: you will need to ensure the build tools from the development enviroment are on your path.
(as covered in DEVENV.md)



Note: 
Specific directories and examples are mentioned in these documents.
however, most can be changed to your own requirements, with simple overrides.
but this is not covered extensively here, to keep things clear and simple.


# install Linux development tools 
```
    sudo apt install cmake git llvm clang g++-10-arm-linux-gnueabihf 
```
this is debian package manager, similar with pacman etc on other distros

(although this is v10 of g++ others will likely work)


# install macOS development using homebrew
homebrew is useful package manager for macos for many open source tools.
highly recommended :)  see https://brew.sh



```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install cmake git llvm pkg-config arm-linux-gnueabihf-binutils

```
(some installs may need gcc-arm-embedded)


## mac m1 - homebrew config
place the following in .zshrc
```
export PATH=/opt/homebrew/bin:"${PATH}"
```

## intel macs - homebrew config 
place the following in .zshrc/.bashrc as appropiate.


```
export PATH=/usr/local/bin:"${PATH}"
```




# setup requirements for build

we need a copy of the build root for the SSP to build
this is detailed in this post:
https://forum.percussa.com/t/update-13072022-superbooth-2022-sd-card-image-fixes-for-usb-audio-sample-rate-switching-asio-support/1556

we need to download from :
https://sw13072022.s3.us-west-1.amazonaws.com/arm-rockchip-linux-gnueabihf_sdk-buildroot.tar.gz


unzip into `~/buildroot` e.g.

```
mkdir ~/buildroot
cd ~/buildroot
mv ~/Downloads/arm-rockchip-linux-gnueabihf_sdk-buildroot.tar.gz  .
tar xzf arm-rockchip-linux-gnueabihf_sdk-buildroot.tar.gz
```

decompression (gz) may not be necessary on some OS versions or browsers, as they may automatically unzip.
if its just .tar use.
```
tar xf arm-rockchip-linux-gnueabihf_sdk-buildroot.tar
```

if all is ok, then we will see
```
% ls ~/buildroot/arm-rockchip-linux-gnueabihf_sdk-buildroot/libexec 
awk     c++-analyzer    ccc-analyzer    gcc
```

note: this directory can be overriden using environment var (if you need to..)
```
export SSP_BUILDROOT=$HOME/buildroot/ssp/arm-rockchip-linux-gnueabihf_sdk-buildroot
```






# testing by building examples 


first we will just build the example that is included to get used to the build system.
(then we will create our own module :) )

### STEP 1 - prepare the build (examples)
assuming we are using the ssp-sdk examples as above
so are in `~/projects/ssp-sdk`

```
cd examples
mkdir build 
cd build 
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=../xcSSP.cmake .. 
```



### STEP 2 - compile (examples) 

the moment we have been building up to...actually compiling the module! 

```
cmake --build . -- -j 4 
```

voila, we have build the modules

you will see that whilst building, it reports the targets... 
aka, the modules that you are going to want to copy to your SSP 


