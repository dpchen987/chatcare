# coding:utf-8

import re
import os
from setuptools import Extension, setup, find_packages
from Cython.Build import cythonize

from chatcare2 import __version__

pkg_name = 'chatcare2'


def main(use_cython=False):
    # TODO: 编译没问题，但是运行时pydantic的数据模型报错，未来解决
    # 暂时不编译data_model,  需把该模块加到setup()的packages里面
    extensions = [
        Extension(f'{pkg_name}/*.so', [f"{pkg_name}/*.py"]),
        Extension(f'{pkg_name}/chains/*.so', [f"{pkg_name}/chains/*.py"]),
        Extension(f'{pkg_name}/embeddings/*.so', [f"{pkg_name}/embeddings/*.py"]),
        Extension(f'{pkg_name}/utils/*.so', [f"{pkg_name}/utils/*.py"]),
    ]
    if use_cython:
        ext_modules = cythonize(
            extensions,
            compiler_directives=dict(always_allow_keywords=True),
            language_level=3)
        # 解决 pydantic 的问题后，在ext_modules里面编译data_model，
        # 则 packages=[]
        packages = []  ## 防止把其它.py 文件也打包到.whl文件里面
    else:
        ext_modules = []
        packages = [pkg_name]
    print('sssss', packages)
    setup(
        name=pkg_name,
        version=__version__,
        description='chatcare',
        author='',
        author_email='',
        url='',
        packages=packages,
        ext_modules=ext_modules,
        entry_points={
            'console_scripts': [
                'chatcare=chatcare2.webapi:run_api',
            ]
        },
    )


if __name__ == '__main__':
    # set False if no need to cythonize
    use_cython = True
    main(use_cython)
