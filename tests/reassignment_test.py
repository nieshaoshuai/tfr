import numpy as np
import os

from tfr.analysis import split_to_frames, read_frames
from tfr.spectrogram import create_window
from tfr.reassignment import chromagram, shift_right, arg, reassigned_spectrogram
from tfr.tuning import Tuning

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def test_shift_right():
    assert np.allclose(shift_right(np.array([[1, 2, 3]])), np.array([0, 1, 2]))

def test_chromagram_on_single_tone_should_have_peak_at_that_tone():
    pitch = 12 + 7 # G5
    f = Tuning().pitch_to_freq(pitch)
    fs = 44100
    x = sine(sample_time(0, 1, fs=fs), freq=f)
    frame_size = 4096
    hop_size = 2048
    output_frame_size = hop_size
    window = create_window(frame_size)
    x_frames, x_times = split_to_frames(x, frame_size=frame_size, hop_size=hop_size, fs=fs)
    bin_range = [-48, 67]
    x_chromagram = chromagram(x_frames, window, x_times, fs=fs,
        frame_size=frame_size, output_frame_size=output_frame_size, to_log=True,
        bin_range=bin_range, bin_division=1)

    max_bin_expected = pitch - bin_range[0]
    max_bin_actual = x_chromagram.mean(axis=0).argmax()

    assert x_chromagram.shape == (22, 115)
    assert max_bin_actual == max_bin_expected

def test_arg():
    values = np.array([-5.-1.j, -1.-5.j,  2.-2.j,  3.+4.j,  2.+0.j,  2.-5.j, -3.-3.j,
       -3.+1.j, -2.-5.j,  0.+2.j])
    args = arg(values)
    expected_args=np.array([0.53141648, 0.71858352, 0.875 , 0.14758362, 0.,
        0.81055947, 0.625 , 0.44879181, 0.68944053, 0.25])
    assert np.allclose(args, expected_args)

def test_reassigned_spectrogram_values_should_be_in_proper_range():
    frame_size = 4096
    output_frame_size = 1024
    audio_file = os.path.join(DATA_DIR, 'she_brings_to_me.wav')
    x_frames, x_times, fs = read_frames(audio_file, frame_size=frame_size)
    w = create_window(frame_size)
    X_r = reassigned_spectrogram(x_frames, w, x_times, frame_size, output_frame_size, fs, to_log=True)
    assert np.all(X_r >= -120), 'min value: %f should be >= -120' % X_r.min()
    assert np.all(X_r <= 0), 'max value: %f should be <= 0' % X_r.max()

def test_reassigned_chromagram_values_should_be_in_proper_range():
    frame_size = 4096
    output_frame_size = 1024
    audio_file = os.path.join(DATA_DIR, 'she_brings_to_me.wav')
    x_frames, x_times, fs = read_frames(audio_file, frame_size=frame_size)
    w = create_window(frame_size)
    X_r = chromagram(x_frames, w, x_times, fs, frame_size, output_frame_size, to_log=True)
    assert np.all(X_r >= -120), 'min value: %f should be >= -120' % X_r.min()
    assert np.all(X_r <= 0), 'max value: %f should be <= 0' % X_r.max()

# --- helper functions ---

def sample_time(since, until, fs=44100.):
    '''
    Generates time sample in given interval [since; until]
    with given sampling rate (fs).
    '''
    return np.arange(since, until, 1. / fs)

def sine(t, freq=1., amplitude=1., phase=0.):
    '''
    Samples the sine function given the time samples t,
    frequency (Hz), amplitude and phase [0; 2 * np.pi).
    '''
    return amplitude * np.sin(2 * np.pi * freq * t + phase)
