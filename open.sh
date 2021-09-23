#cuDNN
CUDA_HOME=/usr/local/cuda
FFMPEG_HOME=/home/n200/library/ffmpeg/build
OPENCV_HOME=/home/n200/library/opencv/release
#BAZEL_HOME=/home/n200/library/bazel

export OPENPOSE_ROOT=/home/library/openpose
export PATH=$CUDA_HOME/bin:$FFMPEG_HOME/bin:$BAZEL_HOME/bin:$OPENCV_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$OPENCV_HOME/lib:$FFMPEG_HOME/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/home/n200/library/opencv-3.4/release/lib/python2.7/dist-packages:$PYTHONPATH
export PYTHONPATH=/home/n200/library/PyOpenPose/build/PyOpenPoseLib:$PYTHONPATH

# Add value
#FFMPEG
FFMPEG_HOME=/home/n200/library/ffmpeg/build

# Edit PATH
export PATH=$FFMPEG_HOME/bin:$PATH





#LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$FFMPEG_HOME/lib:$LD_LIBRARY_PATH

export PKG_CONFIG_PATH=$FFMPEG_HOME/lib/pkgconfig:$PKG_CONFIG_PATH


export CUDA_INSTALL_DIR=/usr/local/cuda
export CUDNN_INSTALL_DIR=/usr/local/cuda
# <<< conda init <<<
#export PYTHONPATH=/home/n200/A70417/model:$PYTHONPATH
export SCONS_PATH=/home/n200/scons-2.1.0
export SCONS_LIB_DIR=$SCONS_PATH/engine
export JSONCPP_PATH=/home/n200/jsoncpp-src-0.5.0


export LD_LIBRARY_PATH=/usr/local/cuda-9.0/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/lib/pkgconfig
export PKG_CONFIG_PATH







__conda_setup="$(CONDA_REPORT_ERRORS=false '/home/n200/anaconda2/bin/conda' shell.bash hook 2> /dev/null)"
if [ $? -eq 0 ]; then
    \eval "$__conda_setup"
else
    if [ -f "/home/n200/anaconda2/etc/profile.d/conda.sh" ]; then
# . "/home/n200/anaconda2/etc/profile.d/conda.sh"  # commented out by conda initialize
        CONDA_CHANGEPS1=false conda activate base
    else
        \export PATH="/home/n200/anaconda2/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda init <<<
export PYTHONPATH=/home/n200/pytorch/build:/usr/local:$PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/n200/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/n200/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/home/n200/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/n200/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup

eval "$(conda shell.bash hook)"
conda activate test
python3 main.py
