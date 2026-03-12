        # ai-experimental-critic

        Rule-based critique engine for experiment proposals identifying missing controls and biases

        ## Why this exists

        Experiment design is where scientific rigor lives or dies. This tool applies systematic critique rules to identify missing controls, statistical issues, confounding variables, and bias risks in experiment proposals — the kind of review a senior PI would provide.

        ## Features

        - 10+ critique rules covering controls, randomization, blinding, and statistics
- Severity-rated findings (critical, warning, info)
- Structured JSON critique reports
- Support for plain text and structured proposal inputs
- Extensible rule engine for custom domain rules

        ## Install

        ```bash
        pip install -e ".[dev]"
        ```

        ## Quickstart

        ```bash
        python -m experimental_critic --help
        python -m experimental_critic.cli critique --input demo_data/proposal_1.json
        ```

        ## Demo data

        Sample data is provided in `demo_data/` for immediate testing without external dependencies.

        ## Limitations

        - Not intended for clinical use
- Uses lightweight heuristics and demo data
- Not a substitute for expert biological interpretation

        ## Roadmap

        - Add more comprehensive test datasets
- Optional LLM integration for enhanced analysis
- Performance benchmarking and optimization

        ## License

        MIT
