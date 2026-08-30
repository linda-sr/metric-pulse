import argparse
import logging
import sys

from load import run_load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("run_pipeline")


def main():
    parser = argparse.ArgumentParser(description="MetricPulse ELT pipeline runner")
    parser.add_argument(
        "--stage",
        choices=["extract", "load", "full"],
        default="full",
        help="Which stage to run (default: full extract+load)",
    )
    parser.add_argument(
        "--fail-on-errors",
        action="store_true",
        help="Exit non-zero if any records failed validation",
    )
    args = parser.parse_args()

    try:
        if args.stage in ("extract", "full"):
            from extract import run_extraction
            logger.info("Running extraction stage...")
            extracted = run_extraction()
            total_errors = sum(len(v) for v in extracted["errors"].values())
            if total_errors > 0:
                logger.warning(f"Extraction completed with {total_errors} validation errors")
                if args.fail_on_errors:
                    logger.error("Failing due to --fail-on-errors flag")
                    sys.exit(1)

        if args.stage in ("load", "full"):
            logger.info("Running load stage...")
            counts = run_load()
            logger.info(f"Load complete. Row counts: {counts}")

        logger.info("Pipeline run finished successfully.")

    except Exception as e:
        logger.error(f"Pipeline run failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()