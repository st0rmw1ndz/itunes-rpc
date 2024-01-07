# iTunes RPC

Shows the current track in iTunes on Discord. Best suited for tracks that have proper metadata.

> [!NOTE]
> This is a major work-in-progress. Expect bugs and changes.

## What works?

- Executing the program and reading data from iTunes
- Uploading the album artwork to Imgur
- Displaying that data on Discord

## What needs to work?

- More image uploader support, and use a proper uploader abstract class system
  - Platforms to be added: [OwO]("https://whats-th.is"), [Catbox]("https://catbox.moe").
- Configuration options, such as the image to use when idling, and the idling string
- Command line interface to provide options as well

This shows a button to view the song on Last.fm, if it exists. However, it does not scrobble your music. If you'd like to have this functionality, I'd recommend the **Last.fm Desktop Scrobbler**. See [here](https://www.last.fm/about/trackmymusic) for more information.