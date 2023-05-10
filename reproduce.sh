#!/bin/bash
rl_checkpoint=0.617898_11_358234.pth
python bin/ensemble.py config/RRG/baseline-mimic.yml \
            dataset.seq.processing=ifcc_clean_report \
            dataset.image.root=${HOME}/Data/mimic-cxr/2.0.0/RRG/mimic-cxr/findings/ \
            dataset.seq.root=${HOME}/Data/mimic-cxr/2.0.0/RRG/mimic-cxr/findings/ \
            dataset.seq.file=findings.tok \
            dataset.seq.tokenizer_max_len=128 \
            dataset.image.file=image.tok \
            dataset.image.image_path=/home/alalbiol/Data/mimic-cxr/2.0.0/files512 \
            dataset.image.multi_image=3 \
            model.proto=RRG_SCST \
            model.top_k=0 \
            model.scores_weights='[0.01,0.495,0.495]' \
            model.scores_args='[{},{reward_level: partial}]' \
            model.scores=[bertscore,radgraph] \
            model.use_nll=true \
            model.cnn.backbone=densenet121 \
            model.cnn.visual_embedding_dim=1024 \
            ensemblor.batch_size=16 \
            ensemblor.beam_width=2 \
            ensemblor.metrics='[bertscore,radgraph,chexbert,rougel]' \
            ensemblor.splits=[validate,test] \
            ensemblor.ckpt=${rl_checkpoint} \
            ckpt_dir=${HOME}/checkpoints \
            name=emnlp22_rl_findings_bertscore_128