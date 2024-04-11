while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --openai_key)
        OPENAI_KEY="$2"
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
if [ -z "$OPENAI_KEY" ]; then
    echo "Error: Please provide --openai_key flag with a value."
    exit 1
fi

if conda info --envs | grep -q luna; then echo "luna already exists"; else conda create -y -n luna python=3.9; fi

python init_n_run.py --openai_key "$OPENAI_KEY"
