"""MetricX-24 regression model (inference only).

Adapted from google-research/metricx `metricx24/models.py` (Copyright 2024 Google LLC, Apache License 2.0):
https://github.com/google-research/metricx. Training, model-parallel and CUDA-specific branches removed;
the scoring computation (single dummy decoder step, logit of token 250089, clamp to [0, 25]) is unchanged.
Lower scores are better.
"""
from __future__ import annotations

import copy

import torch
from torch import nn
from transformers.models.mt5.modeling_mt5 import MT5Config, MT5PreTrainedModel, MT5Stack

SCORE_TOKEN_ID = 250089  # <extra_id_10>


class MT5ForRegression(MT5PreTrainedModel):
    def __init__(self, config: MT5Config):
        super().__init__(config)
        self.model_dim = config.d_model
        self.shared = nn.Embedding(config.vocab_size, config.d_model)
        enc_cfg = copy.deepcopy(config)
        enc_cfg.is_decoder, enc_cfg.use_cache, enc_cfg.is_encoder_decoder = False, False, False
        self.encoder = MT5Stack(enc_cfg, self.shared)
        dec_cfg = copy.deepcopy(config)
        dec_cfg.is_decoder, dec_cfg.is_encoder_decoder = True, False
        dec_cfg.num_layers = config.num_decoder_layers
        self.decoder = MT5Stack(dec_cfg, self.shared)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        self.post_init()

    @torch.no_grad()
    def score(self, input_ids: torch.LongTensor, attention_mask: torch.Tensor) -> torch.Tensor:
        hidden = self.encoder(input_ids=input_ids, attention_mask=attention_mask, return_dict=True).last_hidden_state
        dec_in = torch.zeros((input_ids.size(0), 1), dtype=torch.long, device=input_ids.device)
        out = self.decoder(input_ids=dec_in, encoder_hidden_states=hidden, encoder_attention_mask=attention_mask,
                           use_cache=False, return_dict=True).last_hidden_state
        if self.config.tie_word_embeddings:
            out = out * (self.model_dim ** -0.5)
        logits = self.lm_head(out)
        return torch.clamp(logits[:, 0, SCORE_TOKEN_ID], 0, 25)


def qe_input(src: str, mt: str) -> str:
    return f"source: {src} candidate: {mt}"


def ref_input(src: str, mt: str, ref: str) -> str:
    return f"source: {src} candidate: {mt} reference: {ref}"
