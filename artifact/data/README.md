# Data folder

- `samples/pcaps/`: a tiny anonymized PCAP snippet for running the end-to-end demo.
  Structure: samples/pcaps/<device_name>/<one_small_idle.pcap> (~5 MB).
- `samples/testCsv/`: A CSV file of traffic for matching tests and a CSV file for building the confusion matrix.
  Structure: samples/testCsv/<part1.csv>, samples/testCsv/<uk_confusion_matrix.csv>, samples/testCsv/<uk_confusion_matrix_2period.csv>
- `cached/period/3_selectDir/`: optional cache of Phase-1 output (after 1.3), used to skip PeriodProcess during demo.
- `cached/preproc/12_featureClusterFilter/`: optional cache of Phase-2 final filtered clusters (after 2.10).
- `cached/signatures/16_keyPacketSignatureWithLSH/`: optional cache of Phase-3 final signatures (after 3.5).
- `cached/merged_signatures/17_signatureMerge/`: optional cache of signature library merged CSV.

If a cache directory exists and is non-empty, `artifact/run_demo.sh` will reuse it to shorten runtime; otherwise, the full pipeline runs from `samples/pcaps/`.
