"""
Class for generating IIIF manifests based on images and metadata.

Usage:
    generator = IiifManifestGenerator(baseUri="http://example.org/manifests/")
    images = [
        {
            "image": "http://example.org/image/123",
            "width": 3000,
            "height": 2000
        },
        ...
    ]
    metadata = [
        {
            "label": "Title",
            "value": "Example Title"
        },
        ...
    ]
    manifest = generator.generate(id="123", label="Example Manifest", images=images, metadata=metadata)
"""

import json
from iiif_prezi3 import Canvas, Manifest, Annotation, AnnotationPage, ResourceItem
class IiifManifestGenerator:

    def __init__(self, *, baseUri: str = "http://example.org/manifests/"):
        """
        Initialize the generator.
        """
        self.baseUri = baseUri

    def generate(self, *, id: str, label: str, images: list, metadata: list, license: str | None = None) -> dict:
        """
        Generate a IIIF Presentation API manifest.
        
        :param id: The ID of the manifest.
        :param label: The label of the manifest.
        :param images: A list of images. Each image should be a dict with the keys 'image', 'width', and 'height'.
        :param metadata: A list of metadata items. Each metadata item should be a dict with the keys 'label' and 'value'.

        :return: A dict representing the manifest.
        """
        identifier = f"{self.baseUri}{id}";
        manifest = Manifest(id=identifier, label=label)
        manifest.items = self.generateImageItems(images, manifestId=identifier)
        manifest.metadata = metadata
        if license:
            manifest.rights = license

        # Return manifest as parsed JSON 
        return json.loads(manifest.json(indent=2))
    
    
    def generateImageItems(self, images: list, manifestId: str) -> list:
        """
        Generate a list of image items following the IIIF Presentation API standard.

        :param images: A list of images. Each image should be a dict with the keys 'image', 'width', and 'height'.

        :return: A list of image items.
        """
        items = []
        for i, image in enumerate(images):
            canvasId = f"{manifestId}/image/{i}/canvas"
            canvas = Canvas(
                id=canvasId,
                width=int(image['width']),
                height=int(image['height'])
            )
            service = {
                "id": image['image'],
                "type": "ImageService3",
                "profile": "level2"
            }
            annotation = Annotation(
                type="Annotation",
                id=canvasId + "/annotation",
                target=canvasId
            )
            annotation.motivation = "painting"
            annotation.body = ResourceItem(service=[service], id=image['image']+"/full/max/0/default.jpg", type="Image", format="image/jpeg", width=int(image['width']), height=int(image['height']))
            annotationPage = AnnotationPage(id=canvasId+"/page",type='AnnotationPage')
            annotationPage.items = [annotation]
            canvas.items = [annotationPage]
            items.append(canvas)
        return items