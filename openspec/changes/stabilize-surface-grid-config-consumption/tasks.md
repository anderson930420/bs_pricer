## 1. App Boundary Helper

- [x] 1.1 Add a helper that converts canonical `GRID_CONFIG` values into surface grid defaults and axes.
- [x] 1.2 Update the Streamlit app to consume the helper instead of stale grid key names.

## 2. Regression Coverage

- [x] 2.1 Add tests proving canonical `GRID_CONFIG` keys drive the helper output.
- [x] 2.2 Add tests proving stale keys are not required.
- [x] 2.3 Add a test proving `surface.py` does not import `config.py`.
