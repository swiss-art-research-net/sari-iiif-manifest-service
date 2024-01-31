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
class IiifManifestGenerator:

    def __init__(self, *, baseUri: str = "http://example.org/manifests/"):
        """
        Initialize the generator.
        """
        self.baseUri = baseUri

    def generate(self, *, id: str, label: str, images: list, metadata: list) -> dict:
        """
        Generate a IIIF Presentation API manifest.
        
        :param id: The ID of the manifest.
        :param label: The label of the manifest.
        :param images: A list of images. Each image should be a dict with the keys 'image', 'width', and 'height'.
        :param metadata: A list of metadata items. Each metadata item should be a dict with the keys 'label' and 'value'.

        :return: A dict representing the manifest.
        """
        manifest = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": f"{self.baseUri}{id}",
            "items": [],
            "type": "Manifest",
            "label": {
                "none": [label]
            },
            "metadata": metadata,
        }
        manifest['items'] = self.generateImageItems(images)
        return manifest
    
    def generateImageItems(self, images: list) -> list:
        """
        Generate a list of image items following the IIIF Presentation API standard.

        :param images: A list of images. Each image should be a dict with the keys 'image', 'width', and 'height'.

        :return: A list of image items.
        """
        items = []
        for i, image in enumerate(images):
            canvas = {
                "id": f"{self.baseUri}image/{i}/canvas",
                "type": "Canvas",
                "width": int(image['width']),
                "height": int(image['height']),
                "items": [{
                        "id": f"{self.baseUri}image/{i}/canvas/page",
                        "type": "AnnotationPage",
                        "items": [{
                            "id": f"{self.baseUri}image/{i}/canvas/page/annotation",
                            "type": "Annotation",
                            "motivation": "painting",
                            "body": {
                                "id": f"{image['image']}/full/max/0/default.jpg",
                                "type": "Image",
                                "format": "image/jpeg",
                                "width": int(image['width']),
                                "height": int(image['height']),
                                "service": [{
                                    "id": image['image'],
                                    "profile": "level1",
                                    "type": "ImageService3"
                                }]
                            },
                            "target": f"{self.baseUri}image/{i}/canvas"
                        }]
                    }]
            }
            items.append(canvas)
        return items