import torch
import torch.nn as nn
from mamba_ssm import Mamba

class SentinelMamba(nn.Module):
    def __init__(self, d_model, d_state, d_conv, expand, num_classes):
        super(SentinelMamba, self).__init__()
        self.mamba = Mamba(
            d_model=d_model,
            d_state=d_state,
            d_conv=d_conv,
            expand=expand,
        )
        self.fc = nn.Linear(d_model, num_classes)

    def forward(self, x):
        # x.shape: (batch_size, sequence_length, d_model)
        mamba_out = self.mamba(x)
        # mamba_out.shape: (batch_size, sequence_length, d_model)
        
        # We can take the output from the last token in the sequence
        last_token_out = mamba_out[:, -1, :]
        
        # Or we can average over the sequence length
        # avg_out = mamba_out.mean(dim=1)
        
        output = self.fc(last_token_out)
        return output

# Example usage:
if __name__ == '__main__':
    batch_size = 1
    sequence_length = 100
    d_model = 768  # For example, BERT base dimension
    d_state = 16
    d_conv = 4
    expand = 2
    num_classes = 2  # Binary classification for sentinel ("go" vs "no-go")

    model = SentinelMamba(d_model, d_state, d_conv, expand, num_classes)
    
    # Dummy input tensor
    input_tensor = torch.randn(batch_size, sequence_length, d_model)
    
    output = model(input_tensor)
    
    print("Input shape:", input_tensor.shape)
    print("Output shape:", output.shape)
    print("Output:", output)
