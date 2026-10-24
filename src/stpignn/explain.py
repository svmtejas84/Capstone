"""Shared Captum adapter for STPIGNN input attributions."""
import torch


class CaptumGNNWrapper(torch.nn.Module):
    def __init__(self, base_model, edge_index, edge_attr):
        super().__init__()
        self.base_model = base_model
        self.register_buffer("edge_index", edge_index)
        self.register_buffer("edge_attr", edge_attr)

    def forward(self, x_tensor):
        with torch.set_grad_enabled(True):
            out = self.base_model(x_seq=x_tensor, edge_index=self.edge_index, edge_attr=self.edge_attr)
            return torch.mean(out, dim=1)
