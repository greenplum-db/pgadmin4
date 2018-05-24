## Building

### Prerequisites
* [Docker](https://www.docker.com/)
* [Python Virtual Environment](https://docs.python.org/3/library/venv.html) for python < 3.3

### Create the virtual environment 
1. `cd` into the electron folder of the project
1. Execute the following command to create the distributable version of Python
    ```bash
    $ python -m venv --copies venv
    ```
1. Install all packages needed by the application
    ```bash
    $ venv/bin/pip install -r ../requirements.txt
    ```

### Linux
1. `cd` into the root directory of the project.
1. Execute the `./electron/scripts/build-linux` script in the corresponding docker image to compile utilities (python, javascript) to be bundled with the application.
   ```
   $ docker run -v $PWD:$PWD -w $PWD --rm -t python:3.6 ./electron/scripts/build-linux.sh
   ```

   The linux distributable will be found in the `out/make` directory of the previous electron folder.

### Mac

#### Pre requirements
* [HomeBrew](https://brew.sh/)

#### Steps
1. Install git
`brew install git`
1. Install python environment
    ```bash
    $ brew install pyenv sqlite3
    $ pyenv init
    $ eval "$(pyenv init -)"
    $ git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
    $ eval "$(pyenv init -)"
    $ pyenv install 3.6.5
    $ pyenv virtualenv 3.6.5 python36
    $ pyenv activate python36
    $ mkdir workspace && cd workspace
    $ git clone https://github.com/greenplum-db/pgadmin4.git
    $ brew install node@8
    $ brew install yarn --without-node
    $ git checkout electron
    ```
1. Compile the application using the following command
```bash
$ ./electron/scripts/build-darwin.sh
```

### Windows

#### Pre requirements
* Python 2.7 installed(with virtual env and pip) 
* [Compilation with MSVC for Python](https://www.microsoft.com/en-gb/download/details.aspx?id=44266)


#### Installation steps

Open powershell and run the script in `.\electron\scripts\build-windows.sh`