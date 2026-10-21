/** Real photo credits (Problem 11). CC BY / CC BY-SA require attribution + a link to the
 * license; listing them here, out of the way but one click from anywhere, satisfies that without
 * cluttering the page itself. */
const PHOTO_CREDITS = [
  {
    caption: 'Harkness Tower',
    author: 'ajay_suresh',
    authorUrl: 'https://www.flickr.com/people/83136374@N05',
    license: 'CC BY 2.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/2.0/',
  },
  {
    caption: 'Sterling Memorial Library',
    author: 'Christian David',
    authorUrl: 'https://commons.wikimedia.org/wiki/User:Espandero',
    license: 'CC BY-SA 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0/',
  },
  {
    caption: 'Old Campus',
    author: 'John Phelan',
    authorUrl: 'https://commons.wikimedia.org/wiki/User:Faolin42',
    license: 'CC BY-SA 3.0',
    licenseUrl: 'https://creativecommons.org/licenses/by-sa/3.0/',
  },
  {
    caption: 'Beinecke Rare Book & Manuscript Library',
    author: 'Karlfonza',
    authorUrl: 'https://commons.wikimedia.org/wiki/User:Karlfonza',
    license: 'CC BY-SA 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0/',
  },
  {
    caption: 'Woolsey Hall (c. 1905 postcard)',
    author: 'Unknown',
    authorUrl: null,
    license: 'Public domain',
    licenseUrl: null,
  },
]

export default function Footer() {
  return (
    <footer className="footer">
      <img src="/campus/woolsey-hall.jpg" alt="Woolsey Hall, Yale University, c. 1905" className="footer__photo" />
      <p>Campus Customs: made-to-order Yale merch, designed on campus.</p>
      <p className="footer__small">A class project. Not affiliated with Yale University.</p>
      <details className="credits">
        <summary>Photo credits</summary>
        <ul className="credits__list">
          {PHOTO_CREDITS.map((c) => (
            <li key={c.caption}>
              {c.caption} —{' '}
              {c.authorUrl ? (
                <a href={c.authorUrl} target="_blank" rel="noreferrer">
                  {c.author}
                </a>
              ) : (
                c.author
              )}
              , Wikimedia Commons,{' '}
              {c.licenseUrl ? (
                <a href={c.licenseUrl} target="_blank" rel="noreferrer">
                  {c.license}
                </a>
              ) : (
                c.license
              )}
            </li>
          ))}
        </ul>
      </details>
    </footer>
  )
}
