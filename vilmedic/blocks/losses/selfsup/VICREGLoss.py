import torch
import torch.nn as nn
import torch.nn.functional as F


class VIGREGLoss(nn.Module):
    def __init__(self,
                 sim_loss_weight: float = 25.0,
                 var_loss_weight: float = 25.0,
                 cov_loss_weight: float = 1.0,
                 **kwargs):
        super().__init__()
        self.sim_loss_weight = sim_loss_weight
        self.var_loss_weight = var_loss_weight
        self.cov_loss_weight = cov_loss_weight

    def forward(self, z1: torch.Tensor,
                z2: torch.Tensor,
                ) -> torch.Tensor:
        """Computes VICReg's loss given batch of projected features z1 from view 1 and
        projected features z2 from view 2.
        Args:
            z1 (torch.Tensor): NxD Tensor containing projected features from view 1.
            z2 (torch.Tensor): NxD Tensor containing projected features from view 2.
        Returns:
            torch.Tensor: VICReg loss.
        """

        sim_loss = VIGREGLoss.invariance_loss(z1, z2)
        var_loss = VIGREGLoss.variance_loss(z1, z2)
        cov_loss = VIGREGLoss.covariance_loss(z1, z2)

        loss = self.sim_loss_weight * sim_loss + self.var_loss_weight * var_loss + self.cov_loss_weight * cov_loss
        return loss

    @staticmethod
    def invariance_loss(z1: torch.Tensor, z2: torch.Tensor) -> torch.Tensor:
        """Computes mse loss given batch of projected features z1 from view 1 and
        projected features z2 from view 2.
        Args:
            z1 (torch.Tensor): NxD Tensor containing projected features from view 1.
            z2 (torch.Tensor): NxD Tensor containing projected features from view 2.
        Returns:
            torch.Tensor: invariance loss (mean squared error).
        """

        return F.mse_loss(z1, z2)

    @staticmethod
    def variance_loss(z1: torch.Tensor, z2: torch.Tensor) -> torch.Tensor:
        """Computes variance loss given batch of projected features z1 from view 1 and
        projected features z2 from view 2.
        Args:
            z1 (torch.Tensor): NxD Tensor containing projected features from view 1.
            z2 (torch.Tensor): NxD Tensor containing projected features from view 2.
        Returns:
            torch.Tensor: variance regularization loss.
        """

        eps = 1e-4
        std_z1 = torch.sqrt(z1.var(dim=0) + eps)
        std_z2 = torch.sqrt(z2.var(dim=0) + eps)
        std_loss = torch.mean(F.relu(1 - std_z1)) + torch.mean(F.relu(1 - std_z2))
        return std_loss

    @staticmethod
    def covariance_loss(z1: torch.Tensor, z2: torch.Tensor) -> torch.Tensor:
        """Computes covariance loss given batch of projected features z1 from view 1 and
        projected features z2 from view 2.
        Args:
            z1 (torch.Tensor): NxD Tensor containing projected features from view 1.
            z2 (torch.Tensor): NxD Tensor containing projected features from view 2.
        Returns:
            torch.Tensor: covariance regularization loss.
        """

        N, D = z1.size()

        z1 = z1 - z1.mean(dim=0)
        z2 = z2 - z2.mean(dim=0)
        cov_z1 = (z1.T @ z1) / (N - 1)
        cov_z2 = (z2.T @ z2) / (N - 1)

        diag = torch.eye(D, device=z1.device)
        cov_loss = cov_z1[~diag.bool()].pow_(2).sum() / D + cov_z2[~diag.bool()].pow_(2).sum() / D
        return cov_loss

    def __repr__(self):
        return "ConVIRTLoss(\n" + \
               "\t(sim_loss_weight): {}\n".format(self.sim_loss_weight) + \
               "\t(var_loss_weight): {}\n".format(self.var_loss_weight) + \
               "\t(cov_loss_weight): {}\n".format(self.cov_loss_weight) + \
               ")"
