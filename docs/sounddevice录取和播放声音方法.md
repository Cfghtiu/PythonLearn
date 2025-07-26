# sounddevice录取和播放声音方法
## 安装
库名为: `sounddevice`  
可用`pip install sounddevice`安装

## 常见参数
- **samplerate**: 采样率，每秒采样的次数，单位是Hz，常见值：44100Hz
- **frames**: 帧数，即采样的次数，一个采样点对应一个帧，那么录制两秒的帧数就是samplerate*2
- **channels**: 声道数，1为单声道，2为双声道，选2能让声音有立体声
- **dtype**: 决定了每个采样点的精度，常见值：int16, int32, float32

## 最简案例
假如你要播放example.wav
```python
import sounddevice as sd
import wave
import numpy as np
wav = wave.open("example.wav", "r")  # 打开文件
frames = wav.readframes(wav.getnframes())  # 读取所有帧
data = np.frombuffer(frames, dtype=np.int16)  # 转换为数组
sd.play(data, blocking=True)  # 堵塞播放
```
如果播放的声音听起来很糊，可以更改dtype从np.int16转到np.int32  
或者自动匹配
```text
dtype_map = {
    1: np.int8,
    2: np.int16,
    4: np.int32
}
dtype = dtype_map[wav.getsampwidth()]
```
## 录音
假设要录制3秒并播放
```python
import sounddevice as sd
print("开始录音3秒")
data = sd.rec(frames=44100*3, samplerate=44100, channels=1, blocking=True)
print("开始播放")
sd.play(data, samplerate=44100, blocking=True)
```

## rec的返回值
返回类型为numpy的二维数组，由channels决定每行的元素数量  
如果channels为1，data的数据就长下面这样
```text
[[ 0.0000000e+00]
 [ 0.0000000e+00]
 [-3.0517578e-05]
 ...
 [ 2.3773193e-02]
 [ 1.1810303e-02]
 [-3.5705566e-03]]
```
如果channels为2，data的数据就长下面这样
```text
[[ 0.0000000e+00  0.0000000e+00]
 [-3.0517578e-05  0.0000000e+00]
 [ 0.0000000e+00  0.0000000e+00]
 ...
 [ 1.6479492e-03  1.6479492e-03]
 [ 1.3122559e-03  1.3427734e-03]
 [ 1.1596680e-03  1.1901855e-03]]
```
第一列为左声道，第二列为右声道

## 保存文件
假设录的音要保存
```python
import wave
import numpy as np
import sounddevice as sd
print("开始录音3秒")
data = sd.rec(frames=44100*3, samplerate=44100, channels=1, blocking=True, dtype=np.int16)
with wave.open("example.wav", 'w') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)  # 通过dtype_map查看int16对应2
    wav.setframerate(44100)
    # 转换数据类型并保存
    audio_data = data.tobytes()
    wav.writeframes(audio_data)
```

## 复读机
假设要实时获取麦克风声音并播放，可以用`sd.playrec`，但这次使用流
```python
import sounddevice as sd
# with会调用Stream的start和stop,close方法
with (sd.InputStream(samplerate=44100, channels=1) as inp,
      sd.OutputStream(samplerate=44100, channels=1) as out):
    while True:
        # inp.read返回(data,overflowed)，overflowed为True表示缓冲区溢出了
        # 在长时间不读取时就会溢出，所以要及时处理
        data, _ = inp.read(int(44100*0.1))  # 读取10毫秒数据
        out.write(data)
```

## 回调
如果不想手动开个线程，也可以使用回调函数
```python
import sounddevice as sd

def callback(indata, frames, time, status):
    """
    签名要求(在InputStream的文档中有)：
    callback(indata: numpy.ndarray, frames: int,
         time: CData, status: CallbackFlags) -> None
    """
    out.write(indata.copy())  # indata需要复制，因为它会被InputStream复写
    
inp = sd.InputStream(samplerate=44100, channels=1, callback=callback)
out = sd.OutputStream(samplerate=44100, channels=1)
inp.start()
out.start()
input("stop:")
# 执行stop和close
```
InputStream还有个blocksize参数，决定缓冲区大小，如果设置为samplerate的值，那么callback就会被每秒调用一次