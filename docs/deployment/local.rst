.. _local_infrastructure:

==========================
Local infrastructure setup
==========================

Step 1: Create a Python environment and clone the repository

The ``quantum-serverless`` repository contains some Dockerfiles which make spinning up a test cluster
on your local machine straightforward. The first thing we will do is clone the repository.

.. code-block::
   :caption: Create a minimal environment with only Python installed in it. We recommend using `Python virtual environments <https://docs.python.org/3.10/tutorial/venv.html>`_.

      python3 -m venv /path/to/virtual/environment

.. code-block::
   :caption: Activate your new environment.

      source /path/to/virtual/environment/bin/activate

.. code-block::
   :caption: Note: If you are using Windows, use the following commands in PowerShell.

      python3 -m venv c:\path\to\virtual\environment
      c:\path\to\virtual\environment\Scripts\Activate.ps1

.. code-block::
   :caption: Clone the Quantum Serverless repository.

      cd /path/to/workspace/
      git clone git@github.com:Qiskit-Extensions/quantum-serverless.git

Step 2: Set up Docker

To set up Quantum Serverless on your local machine, you will need to use `docker compose`_.

.. _docker compose: https://docs.docker.com/compose/

Step 3: Initiate the test cluster

Once you have Docker and docker compose installed, you can run the following command from the root of the
``quantum-serverless`` repository to set up the infrastructure:

.. code-block::

        $ docker compose [--profile <PROFILE>] up

The available profiles are `full`, `jupyter`, and `repo`.
The repo profile installs core services and the program repository;
the jupyter profile installs core services and Jupyter Notebook;
and the full profile installs all core services, including logging and
monitorying systems and jupyter.

Step 4: Run a program in the test environment

Once the containers are running, you can simulate a remote cluster with the resources on your
local machine. To create and run programs in this simulated cluster, visit the Jupyter Lab
environment at `localhost:8888` via a web browser. Refer to the :ref:`getting_started` guides
for details about running your program remotely.
