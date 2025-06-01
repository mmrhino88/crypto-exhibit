# crypto-exhibit

Hi, welcome to my repo. This repo highlights the data feeders and a skeleton of the model eval architecture of my crypto trading system. 
If you want to test out the codes, please use the script under `examples\` after completing the prerequisites below!

## Quick Start

### Prerequisites

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Note: the requirements are auto-generated. The repo do not necessarily need the latest package versions. 

2. Create a `keys.env` file in the root directory with your KuCoin API credentials (you can generate these at Kucoin's web portal)
   ```
   KUCOIN_API_KEY=your_api_key_here
   KUCOIN_API_SECRET=your_api_secret_here
   KUCOIN_API_PASSPHRASE=your_api_passphrase_here
   ```

### Testing

Run the example script to see the system in action:

```bash
python examples/run_model_eval.py
```

This will:
- Load hourly prices for the top 3 most liquid futures symbols
- Run a toy momentum signal based on past 20 periods

## Architecture

- `data/` - Data abstraction layer
- `model/` - Alpha models and model eval engine
- `examples/` - Example scripts

Feel free to create an issue or a pull request if you spot any areas for improvement! :)
