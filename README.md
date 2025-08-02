
# ForkCast
![ForkCast Logo](src/webapp/ForkCast.png)

## Restaurant Recommender and Cuisine Type Classifier

---

### Setup conda environment

**Install** conda environment:
```sh
$ conda env create -f conda.yml
```
**Update** the environment with new packages/versions:
1. modify template.yml
2. run `conda env update`:
```sh
$ conda env update --name restaurant-recommend-classifier --file conda.yml --prune
```
`prune` uninstalls dependencies which were removed from conda.yml

**Use** environment:
before working on the project always make sure you have the environment activated:
```sh
$ conda activate restaurant-recommend-classifier
```

**List** all installed environments:
From the base environment run
```sh
$ conda info --envs
```

**Remove** environment:
```sh
$ conda env remove -n restaurant-recommend-classifier
```

See the complete documentation on [managing conda-environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

---

### Project Structure
