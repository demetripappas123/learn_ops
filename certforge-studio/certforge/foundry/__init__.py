"""Optional Azure / Foundry integration.

All modules here lazy-import the Azure SDKs and fail safe (return None / base
values) so the core CertForge app runs with zero Azure dependencies installed.
"""
