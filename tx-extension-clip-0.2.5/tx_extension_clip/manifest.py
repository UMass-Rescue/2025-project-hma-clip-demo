from threatexchange.extensions.manifest import ThreatExchangeExtensionManifest

from tx_extension_clip.config import (
    CLIP_NORMALIZED,
    OPEN_CLIP_MODEL_NAME,
    OPEN_CLIP_PRETRAINED,
)
from tx_extension_clip.hasher import CLIPHasher


class CLIPExtensionManifest(ThreatExchangeExtensionManifest):
    """
    CLIP Extension Manifest.
    """

    @classmethod
    def bootstrap(cls):
        """
        Download the model on extension install.
        """
        clip_hasher: CLIPHasher = CLIPHasher(
            model_name=OPEN_CLIP_MODEL_NAME,
            pretrained=OPEN_CLIP_PRETRAINED,
            normalized=CLIP_NORMALIZED,
        )
        clip_hasher.init_model_and_transforms()
