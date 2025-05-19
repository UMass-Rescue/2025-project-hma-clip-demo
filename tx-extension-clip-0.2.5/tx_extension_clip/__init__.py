from tx_extension_clip.manifest import CLIPExtensionManifest
from tx_extension_clip.signal import CLIPSignal

TX_MANIFEST = CLIPExtensionManifest(
    signal_types=(CLIPSignal,),
)
