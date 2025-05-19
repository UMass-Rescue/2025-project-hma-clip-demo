"""
CLIP Signal Type.
"""

import binascii
import typing as t

import numpy as np
from threatexchange.content_type.content_base import ContentType
from threatexchange.content_type.photo import PhotoContent
from threatexchange.signal_type import signal_base

from tx_extension_clip.config import CLIP_DISTANCE_THRESHOLD, CLIP_HASHER
from tx_extension_clip.index import CLIPIndex
from tx_extension_clip.utils.distance import cosine_distance


class CLIPSignal(
    signal_base.SignalType,
    signal_base.BytesHasher,
):
    """
    CLIP Signal Type.
    Article: https://arxiv.org/pdf/2103.00020.pdf
    CLIP is a neural network trained on a variety of (image, text) pairs.
    It can be used to generate image embeddings with semantic similarity, meaning
    that images with similar content will have similar embeddings.
    For example, two different images of cats will have higher cosine similarity
    than an image of a cat and an image of a tree.
    This type of hashing is robust to perceptual differences as long as the
    semantic content is the same.
    """

    INDICATOR_TYPE: str = "HASH_CLIP"

    @classmethod
    def get_content_types(cls) -> t.List[t.Type[ContentType]]:
        return [PhotoContent]

    @classmethod
    def get_index_cls(cls) -> t.Type[CLIPIndex]:
        return TrivialCLIPIndex

    @classmethod
    def validate_signal_str(cls, signal_str: str) -> str:
        if len(signal_str) != 4096:
            raise ValueError(
                f"CLIP hashes must be 4096 characters long. Got {len(signal_str)}"
            )

        return signal_str

    @classmethod
    def hash_from_bytes(cls, bytes_: bytes) -> str:
        """
        Generate a CLIP hash from a bytes object.
        """
        return CLIP_HASHER.hash_from_bytes(bytes_).serialize()

    @classmethod
    def compare_hash(
        cls, hash1: str, hash2: str, threshold: float = CLIP_DISTANCE_THRESHOLD
    ) -> signal_base.SignalComparisonResult:
        """
        Compare two CLIP hashes.
        """
        vec1: np.ndarray = np.frombuffer(binascii.unhexlify(bytes(hash1, 'ascii')), dtype=np.float32)
        vec2: np.ndarray = np.frombuffer(binascii.unhexlify(bytes(hash2, 'ascii')), dtype=np.float32)
        distance: float = cosine_distance(vec1, vec2)
        return signal_base.SignalComparisonResult.from_simple_dist(distance, threshold)

    @staticmethod
    def get_examples() -> t.List[str]:
        return [
            "52dadfbc050dca3d0a42bbbc264704bdb2aa4b3c0770ebbba127ef3b6bbb403be84741bdfd9be73c695f02bdd68a0e3d706cfe3cbe4f98bb210f043c43d29abc8e1b28bd88183c3d0ef445bd8a80133ccf09a53b9339973ceb4fe73cb6f63e3c75619dbcde9c60bcd905263d19bb4a3c110e86bdf67b313dcf94163d8bbfc23b5d4b0abda5875b3c494489bcc94890bcd5bf463d24c90ebdd12356bbebe83b3d1908753d1720b9bba299c7b9fe56e1bb22c97a3b4e96bbbc895967bdcbde523d9441b7bc664d91bbfcb82a3e675b8fbc764da1bbaa4f463c8c70babcaafd843df9d69bbb71c572bdf54d03bc813d833ba4ba06bd1098113d0683debc7b3cbabcd435963a3c2ca73c222c393dbacbd03b71223d3bb5ea813be7080fbe1274493d6efaaabb0f9bc73cb48999bb80f0d2bb50ce75bc1ce160bb7bc9a0bdee20143dcd638a3d679d5f3ce1f01abcd19a7dbd890da33c92724dbcdc8e733d40101f3d2bcd03bd727cfd3bf2d71f3d4ca7b93b08cfcbbc42d2d73c8242873cd8d28ebc46c4bdbcffce9c3cae58423c1621d6ba561789bcbc3c203ce72c013cae39313d193dd7bc940fa73b8e006bba63fcdb3ccf13a33b105731bcc3a812bd0372e43980befcbbaa887aba71e0abbcb3edecbc915788bccf5338bd6ee281bc86eab6bb7f3d29bc98c107bde3ac68bc633e41bcd8d4e83bb0abbbbc225d85bb8c0583bc59a7b9bce5ee3dbc72c3acbcc90c09bd0c4510bc23d2123dd04ab7bce6b6d93c17d984bd76f5633c8f4240b9f79fee3cfdbf383c51d4c3be5977f7bbcf71c2bc2f20ab3c461d263c2019593cc50e523c2680963b08b72bbd5c86cc3c4522d4bc18e0113d3cf758bc9878a6b9b12636bc3c4886bc13c7933cbb7a81bbf4164abc6d80463d4e5afbbcb06d2bba4d8529bc5f4f9fba8ade49bdb42031bda78c12bd84b413bc0ae154bd2e38d8bc7bc850bd87b0763c345b07bd244908bda99ad43c9449b8bc9c4700be008cb3bc147e6bbde34d1bbdf9ae45bc58848cbb510bf43c286ab93bc368113d892aefbcf4b1adbc34b2eabd9b04b93cb7eb34bb402c88bc25c0df3b734221bdbcda763d53f8063d752538bbb2ef2ebce629fbbc5726f3b9c8b299bc54843ebd466e5d3d121d18bce8cd213db029093d4cc3d1ba562e32bd8816413bfc5c34bd2e9596bb3357a43c95c10b3dcd4a343a64eaf83bc6ce5d3be0b2e13b8abd0fbddbcccdbbcd9d553c18b8d8bc443d273ca6233b3c5b7083bd1448f13b823e51bcebca113d77bc953a9f8f46bcfbec953cd652c73d8f838cbc9e5d79bcdff39cbcbbcebb3dce0a82bce63ac7bc4de40abd4624a6bcadb1cebcb62fccbc315f173dc2bd56bb94c11e3d7212e8bc592d043c38ac153d6aae04bcf7059bbb14d6933c520d9cbc0b27f23c13c5a5bc76771b3d375fa6bdb9d4dcbc39edbc3be09f3f3c801c833df094013ccfa6513c34560ebdc4dde1bbfd4396bb2ddb023d6091b6bb7c1dc93b2624ff3c920ab43a8851e93b327d343cee42693d4f7fbfbc61752bbd67c31c3da1c1c5bb2b73c23cce98843c3461febc997bf43cef65d03c456d4a3c4b24043c5351c5ba139aa8bc6103093d52b7c53c871aab3c6586c5bc52c03dbd53782fbcf442853d6dfb7c3d8fe62cbd28bcd3bc2c0e2f3c57b8dbbb0941fd3c2ffaed3bd01a78bc956f76bd047eb4bc3b916a3c61c14abd46baaa3c2b6d5abdc78b29bd25b2f7bc47918abc92b2b33b8d5b33bda921c23ecd8da13b8891c23cf8ec1fbd276ce3bcc6d27dbc870754b9279c80bc674fb73ced1b43bd89a6ae3cc55c4b3d14eb0e3c6f1f1bbc5280a13d6072f93bb0c2763ca53ebfbb34d1fb3c2848483dd601a13c87cf4ebc453aebbbe42ebe3b7275c23a2ae8223c13ef5f3bbeb7aa3c9aca0bbdde7ac9bbb60a453b3fc26c3c2f6c183c3e6b393bf7195d3c46058db97a8b2bbd8087d3bc97f84abdd3fa19bde6b7b43ce420dfbcb29208bd5ac7fbbc812e05bdfc3705bd495a55bc015030bd05f99d3c858319bd67ad9bbc2bf18dbd8290173c434cd3bcfa67143dddbf953c539473bdbae32abdfaea3f3c307f22bd23756abccae6a4bcc8bd2ebdee8cac3cc336683bb291ac3ceaee52bd09d703bc23b606bcc9454bbc4b4e1ebd17f41dbdf95e58bda59a80bd3492b43bf1a3cebcace5933a4a9393bc08a45b3c066b093a11b8823d787b213d6ea6023d8ca1a1bca167353d61f443bc5ad425bd4c785b3d476ba3bc2fa257b818b716bd5a1aa7bccb734a3de515aebce22c97ba7cbf4cbdc930c93caf53133dc28464bc084e91bc62cdd7bbbddf2a3da1f0af3c3abf5ebc000da3bcf765bbbb0efda23da6bbdd3c509d9cbc4fb84cbc9be8de3c4a7b81bc3fbc933d76e3323d628fa53d99e015bcc993f53b896e1e3d233608bdfae8d0bcd1797ebaf646c1bcf6372e3c65dd9bbc2d0f87bd4de91dbb92ce863b01e7d8bbdc91113d1fa3ae3cac8e8b3bac9b07beede1c33bb82ba93b1729f93c16a2193cd18748bdd7e4373dffe41cbc1da20f3d956d9c3c4662debca62341bd1fb9bebcf75b72bd8068563b81f1903d8bf2f4bba58604bc7a64cdbc13b0afbcd93034bc7e76023db0f5b03c56e8173c8d7416bc9e14033bf6b7a73c5695a2bc44a5c93ab447efba6a46113d3ff9573c27580f3d5401a4bb8e3f413d2257e53cf3c5023d55f1133c60efa7bc8b4922bd873f9fbcc4d1e83c6e261cbdd2a4fabcbea112bdab5b003ce396603d2dc0ba3c330dc8bcfe1c4e3cb1b5a8bc37951c3bbd81043df2cf68bca163623cdf73c3bc95782b3d2d297a3d2208cb3c860f8dbc1797b93c8d80ab3cedb1f23d662df0bc7958c1bea0313fbaf6ed063dad07e73c6a3275bb9581323d"  # noqa
        ]


class TrivialCLIPIndex(signal_base.TrivialLinearSearchHashIndex):
    _SIGNAL_TYPE = CLIPSignal
