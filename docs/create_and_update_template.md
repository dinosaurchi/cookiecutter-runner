# Create and update a template repository

## Cookiecutter directory

Templates are all placed in [`templates`](/templates)

A cookiecutter directory must have the following structure:
```
example_template/
  |
  |_cookiecutter.json (declare all variables and the default values)
  |
  |_hooks (optional)
  |   |
  |   |_ pre_gen_project.py (script to run before project generating)
  |   |
  |   |_ post_gen_project.py (script to run after project generating)
  |
  |_{{cookiecutter.project_name}} (your source code template)
```

## cookiecutter.json

Declare all the the mapping to fill the `{{cookiecutter.variable_name}}` placeholders

```json
{
  "project_name": "example_project",
  "variable_1": "value_1",
  "variable_2": "value_x",
  ...
}
```

## Template directory

You template directory usually has name as a placeholder `{{cookciecutter.project_name}}`

In order to utilize all features (execute template tests inline) of this template tool, a template directory must have the following structure:

```
{{cookiecutter.project_name}}
  |
  |_ .vscode (optional, to have project specified settings for VSCode)
  |
  |_ .github (optional, for CI run with Github Actions)
  |
  |_ .gitignore
  |
  |_ Makefile
  |
  |... (your project files)
```

The `Makefile` must include the following targets:

```makefile
install:
  # Initialize the project environment
lint:
  # Linting/formatting source code
check:
  # Linting, type checks
test:
  # Run tests
```

The `.gitignore` must includes:
- Heavy data paths (if any)
- Virtual environment path (if any)
- Cache paths (if any)

For better experience with `VSCode` when playing around with different templates:
- Add `.vscode` to have project specified formatter, linter, tab-size for each file you open on the Editor
- `VSCode` is smart enough to auto apply different settings for each file, depends on where the file comes from
- In order to use this cool feature, please add the template directory (not the cookiecutter directory) to the workspace of this tool so that `VSCode` can recognize it


## Run existing template

You can modify the template for upgrades, however, as we replaced the template with a lot of `{{cookiecutter.var_name}}` placeholders, it is not guaranteed that we can test the project in this form (with placeholders)

We have an inline solution to execute your tests in the template directory:
```sh
$ cookiecutter-runner --template <path_to_template>
```

## Debug generated project

All projects are generated in `.cookiecutter-runner-cache/` directory

You can enter the target generated project directories and run your debug