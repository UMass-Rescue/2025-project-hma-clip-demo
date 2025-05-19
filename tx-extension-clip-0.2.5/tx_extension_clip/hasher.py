"""
CLIP hashing utilities. Includes a CLIPHasher class that handles generating the CLIP hashes.
"""
from __future__ import annotations

import binascii
import io
import pathlib
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import open_clip
import torch
import torchvision.transforms as transforms
from open_clip.factory import (
    convert_to_custom_text_state_dict,
    load_state_dict,
    resize_pos_embed,
)
from PIL import Image


@dataclass
class CLIPOutput:
    """
    The output of the CLIP hasher.

    We need to make sure to keep the `model_name` and `pretrained` to specify which version
    of the model was used.
    """

    model_name: str
    pretrained: str
    normalized: bool
    hash_vector: Optional[np.ndarray] = None

    def deserialize(self, hex_: str) -> CLIPOutput:
        """Deserializes the CLIP hash from a string.

        Args:
            hex_ (str) : The serialized CLIP hash.

        Returns:
            CLIPOutput: The deserialized CLIP hash.
        """
        bytes_: bytes = binascii.unhexlify(bytes(hex_, "ascii"))
        hash_vector: np.ndarray = np.frombuffer(bytes_, dtype=np.float32)
        return CLIPOutput(
            hash_vector=hash_vector,
            model_name=self.model_name,
            pretrained=self.pretrained,
            normalized=self.normalized,
        )

    def serialize(self) -> bytes:
        """Serializes the CLIP hash to a string.

        Returns:
            bytes: The serialized CLIP hash.
        """
        if self.hash_vector is None:
            raise ValueError("Hash vector is None")
        return str(binascii.hexlify(self.hash_vector.tobytes()), "ascii")


class CLIPHasher:
    """
    The CLIP hasher. Handles the CLIP model and transform pipeline to generate hashes.
    """

    def __init__(self, model_name: str, pretrained: str, normalized: bool = True):
        self.model_name: str = model_name
        self.pretrained: str = pretrained
        self.normalized: bool = normalized

        self._model: Optional[torch.nn.Module] = None
        self._transform: Optional[transforms.Compose] = None

        #this open clip torch issue has been fixed with this merge  https://github.com/mlfoundations/open_clip/pull/595
        #fix_open_clip()

    @property
    def model(self) -> torch.nn.Module:
        """Returns the CLIP model."""
        if self._model is None:
            self.init_model_and_transforms()
        return self._model

    @property
    def transform(self) -> transforms.Compose:
        """Returns the CLIP image transform pipeline."""
        if self._transform is None:
            self.init_model_and_transforms()
        return self._transform

    def init_model_and_transforms(self):
        """Initializes the CLIP model and transform pipeline."""

        # we do not need the training transformations
        self._model, _, self._transform = open_clip.create_model_and_transforms(
            self.model_name, self.pretrained
        )

    def hash_from_file(self, path: pathlib.Path) -> CLIPOutput:
        """Returns the CLIP hash from a file path.

        Args:
            path (pathlib.Path): The path to the file.

        Returns:
            CLIPOutput: The CLIP hash.
        """
        return self.hash_from_file_list([path])[0]

    def hash_from_bytes(self, file_bytes: bytes) -> CLIPOutput:
        """Returns the CLIP hash from a bytes object.

        Args:
            file_bytes (bytes): The bytes object.

        Returns:
            CLIPOutput: The CLIP hash.
        """
        return self.hash_from_bytes_list([file_bytes])[0]

    def hash_from_image(self, image: Image) -> CLIPOutput:
        """Returns the CLIP hash from a PIL Image object.

        Args:
            image (Image): The PIL Image object.

        Returns:
            CLIPOutput: The CLIP hash.
        """
        return self.hash_from_image_list([image])

    def hash_from_file_list(self, paths: List[pathlib.Path]) -> List[CLIPOutput]:
        """Returns the CLIP hash from a list of file paths.

        Args:
            paths (List[pathlib.Path]): The list of file paths.

        Returns:
            List[CLIPOutput]: The CLIP hashes.
        """
        images: List[Image.Image] = [Image.open(path) for path in paths]
        return self.hash_from_image_list(images)

    def hash_from_image_list(self, images: List[Image.Image]) -> List[CLIPOutput]:
        """Returns the CLIP hash from a list of PIL Image objects.

        Args:
            images (List[Image]): The list of PIL Image objects.

        Returns:
            List[CLIPOutput]: The CLIP hashes.
        """
        transformed_images: torch.Tensor = torch.stack(
            [self.transform(image) for image in images]
        )
        with torch.no_grad():
            image_features: torch.Tensor = self.model.visual(transformed_images)
        if self.normalized:
            image_features = torch.nn.functional.normalize(image_features, dim=1)
        return [
            CLIPOutput(
                hash_vector=image_feature.numpy(),
                model_name=self.model_name,
                pretrained=self.pretrained,
                normalized=self.normalized,
            )
            for image_feature in image_features
        ]

    def hash_from_bytes_list(self, file_bytes_list: List[bytes]) -> List[CLIPOutput]:
        """Returns the CLIP hash from a list of bytes objects.

        Args:
            file_bytes_list (List[bytes]): The list of bytes objects.

        Returns:
            List[CLIPOutput]: The CLIP hashes.
        """
        images: List[Image.Image] = [
            Image.open(io.BytesIO(file_bytes)) for file_bytes in file_bytes_list
        ]
        return self.hash_from_image_list(images)

    def get_version_str(self) -> str:
        """Returns a string representing the version of the model used."""
        return f"{self.model_name}-{self.pretrained}-{'normalized' if self.normalized else 'unnormalized'}"


def fix_open_clip():
    """
    This is a fix for an incompatibility between a new version of `transformers` and `open_clip`.
    I hate it.
    Info here: https://github.com/mlfoundations/open_clip/pull/595
    The above PR is merged, but not yet released as of writing this.
    """

    def _load_checkpoint(model, checkpoint_path, strict=True):
        state_dict = load_state_dict(checkpoint_path)
        if "positional_embedding" in state_dict and not hasattr(
            model, "positional_embedding"
        ):
            state_dict = convert_to_custom_text_state_dict(state_dict)
        resize_pos_embed(state_dict, model)
        del state_dict["text.transformer.embeddings.position_ids"]
        incompatible_keys = model.load_state_dict(state_dict, strict=strict)
        return incompatible_keys

    open_clip.factory.load_checkpoint = _load_checkpoint
