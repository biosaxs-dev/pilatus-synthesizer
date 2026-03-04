# coding: utf-8
"""
    GpuInfo.py

    Copyright (c) 2019-2020, Masatsuyo Takahashi, KEK-PF
"""
import sys
import os
import subprocess
import re

class DxdiagInfo:
    def __init__(self):
        import os
        import tempfile
        import subprocess

        self.info_list = []
        path = tempfile.gettempdir()
        # print(path)
        file = path + '/dxdiag.txt'
        ret = subprocess.run(['dxdiag', '/t', file])
        if ret.returncode == 0:
            with open(file) as fh:
                for line in fh.readlines():
                    # print(line)
                    kw = 'Card name:'
                    n = line.find(kw)
                    if n > 0:
                        n += len(kw) + 1
                        self.cardname = line[n:-1]
                        # print(self.cardname)
                        self.info_list.append(line[:-1])
                        break
        else:
            assert False

        os.remove(file)

    def get_info_list(self):
        return self.info_list

def get_cupy_version():
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'cupy'], capture_output=True)
        assert result.returncode == 0
        stdout = result.stdout.decode()
        version_re = re.compile(r'Version: (.+)\r\n')
        m = version_re.search(stdout)
        if m:
            version = tuple(m.group(1).split('+'))
        else:
            version = None
    except:
        version = None
    # print("get_cupy_version: version=", version)
    return version

def get_nvcc_version():
    try:
        result = subprocess.run(['nvcc', '-V'], capture_output=True)
        stdout = result.stdout.decode()
        # print('get_nvcc_version: stdout=', stdout)
        version_re = re.compile('(V\d+\.\d+)\.\d+')
        m = version_re.search(stdout)
        if m:
            version = m.group(1)
        else:
            version = version
    except:
        version = None
    # print('get_nvcc_version: version=', version)
    return version

def get_cuda_version():
    import subprocess
    try:
        import cupy
        import cupy.cuda
        version = (cupy.__version__, cupy.cuda.runtime.runtimeGetVersion())
    except:
        version = None
    # print('get_cuda_version: version=', version)
    return version

class GpuInfo:
    def __init__(self):
        self.get_graphics_card_info()
        self.cuda_path = os.environ.get('CUDA_PATH')
        self.cupy_version = get_cupy_version()
        self.nvcc_version = get_nvcc_version()
        self.cuda_version = get_cuda_version()
        self.cuda_is_availale = self.cuda_version is not None
        try:
            import cupy
            self.cupy_is_installed = True
        except:
            self.cupy_is_installed = False

    def get_graphics_card_info(self):
        from pythoncom import CoInitialize, CoUninitialize
        CoInitialize()      # required inside a thread
        import wmi
        wmi_infos = wmi.WMI().Win32_VideoController()

        # Name = "NVIDIA GeForce GTX 960";
        vp_re = re.compile(r'\s+Name = "(.+)"')
        self.card_infos = []

        exists_compatible = False
        self.index_compatible = None
        for k, i in enumerate(wmi_infos):
            info = str(i)
            m = vp_re.search(info)
            if m:
                name = m.group(1)
            else:
                name = None

            if info.find('NVIDIA') > 0:
                compatible = True
                exists_compatible = True
                if self.index_compatible is None:
                    # set the first-found
                    self.index_compatible = k
            else:
                compatible = False

            self.card_infos.append((name, compatible))

        self.nvidia_compatible = exists_compatible
        k = 0 if self.index_compatible is None else self.index_compatible
        self.card_name = self.card_infos[k][0]
        CoUninitialize()    # required inside a thread

    def check_cupy_cuda_consistency(self):
        cupy_ver_num = self.cupy_version[1].replace('cuda', '')
        non_digit_re = re.compile(r'\D+')
        cuda_ver_num = re.sub(non_digit_re, '', self.nvcc_version)
        return cupy_ver_num == cuda_ver_num

    def cuda_ok(self):
        return self.nvidia_compatible and self.cuda_is_availale

    def cupy_ok(self):
        return self.cuda_ok() and self.cupy_is_installed

    def get_reason_texts(self):
        texts = []

        # GPU Card compatibility
        not_ = '' if self.nvidia_compatible else 'not '
        texts.append(self.card_name + ' is %sNVIDIA compatible.' % not_)
        if not self.nvidia_compatible:
            # unless it is nvidia_compatible, there is no need to add further information.
            return texts

        # CUDA installation
        conn_text = 'And, ' if self.cuda_is_availale == self.nvidia_compatible else 'However, '
        if self.cuda_version is None:
            if self.nvcc_version is None:
                cuda_text = 'CUDA is not found installed.'
            else:
                versions = (self.cupy_version, self.nvcc_version)
                if self.check_cupy_cuda_consistency():
                    cuda_text = 'Something is wrong with Cupy %s and DUDA %s.' % versions
                else:
                    cuda_text = 'Cupy %s is inconsistent with CUDA %s.' % versions
        else:
            cuda_text = 'CUDA %s is installed.' % self.cuda_version[1]
        texts.append(conn_text + cuda_text)

        # CUDA_PATH environ
        cuda_path = self.cuda_path
        if cuda_path is None:
            cuda_path_text = 'CUDA_PATH environment variable is not set, which should have been set to'
            texts.append(cuda_path_text)
            cuda_path_text = r'some value like "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1".'
            texts.append(cuda_path_text)
        else:
            cuda_path_text = 'CUDA_PATH environment variable is set to'
            texts.append(cuda_path_text)
            texts.append('"%s".' % cuda_path)
        return texts
