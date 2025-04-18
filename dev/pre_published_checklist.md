## Published in checklist:
 
1. run 
```
poetry run flake8 src
```

2. in __main__.py comment all out:
```markdown
# Quick debug level setting - uncomment ONE of these lines:
# os.environ['FTML_STUDIO_LOG_LEVEL'] = 'DEBUG'  # Show all debug messages
# os.environ['FTML_STUDIO_LOG_LEVEL'] = 'INFO'     # Show informational messages and above
# os.environ['FTML_STUDIO_LOG_LEVEL'] = 'WARNING'  # Show only warnings and errors
# os.environ['FTML_STUDIO_LOG_LEVEL'] = 'ERROR'    # Show only errors
```

3. run unittest (todo add tox)

4. set version in:
```
# set ftml and ftml-studio
version = "0.1.0a1"
ftml = "^0.1.0a1"

# set in cli/__init__.py
window.setWindowTitle("FTML Studio - v0.1.0a1")
```

5. optional run
```
poetry build
```

7. Check/update read me. 

6. optional run
```
poetry publish
```

## Project Setup:

add to pyproject.py
```
[tool.poetry]
# ... existing configuration
packages = [{ include = "ftml_studio", from = "src" }]
```

create editable install, run:
```
poetry install
```

import like:
```
from ftml_studio.logger import setup_logger
```
