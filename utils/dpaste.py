from aiohttp import ClientSession


async def upload(text: str, slim: bool = True) -> str:
    """
    Upload text to dpaste.org. Deletes 24 hours after creation. Returns a URL to the text.
    """
    async with ClientSession() as session:
        async with session.post("https://dpaste.org/api/", data={"format": "url", "content": text}) as response:
            if response.status != 200:
                return "INTERNAL ERROR OCCURED WHILE UPLOADING!"
            return await response.text("utf-8") + "/slim" if slim else ""
