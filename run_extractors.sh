while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --config)
        CONFIG="$2"
        shift
        shift
        ;;
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Check if --openai_key flag is provided
if [ -z "$CONFIG" ]; then
    echo "Error: Please provide --config flag with a path."
    exit 1
fi

# Call Python script with the provided config file
python init_n_run.py --config "$CONFIG"
