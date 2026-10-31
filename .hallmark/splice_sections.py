# Splice S2 (three verbatim panels), S3 (doctrine/openings), S4 (install + collapse),
# and the footer colophon into docs/index.html, plus their CSS. Idempotent: refuses to run
# if the sections already exist.
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'docs/index.html'
t = open(path, encoding='utf-8').read()
if 'section class="loop"' in t:
    sys.exit('already spliced')

# --- assemble the panels from the generated fragment ---
frag = {}
cur = None
for line in open('.hallmark/panels.py.out', encoding='utf-8').read().split('\n'):
    if line.startswith('==='):
        cur = line[3:-3]
        frag[cur] = []
    elif line and cur:
        frag[cur].append(line)
for k, v in frag.items():
    frag[k] = '\n'.join(v)

html_anchor = '</section>\n\n</main>'
assert html_anchor in t, 'hero anchor missing'

SECTIONS = '''<section class="loop">
  <div class="container">
    <header class="plan">
      <h2>A year in three prints</h2>
      <p class="lead">Captured output of a BALANCED run. Colour is the only stage.</p>
    </header>
    <div class="moments">

      <article class="moment">
        <header class="moment-head">
          <h3><span class="no" aria-hidden="true">01</span> The directive</h3>
          <p class="caption">One big public lever a year. You set it; the court grades it.</p>
        </header>
        <figure class="session" data-print aria-label="The yearly directive menu and the graded result of choosing the KGB crackdown">
          <span class="visually-hidden">The menu carries fourteen public policies in five groups. Choice 10 is graded: economy up 1, order up 7, faith down 3, prestige down 2.</span>
          <pre aria-hidden="true">''' + frag['directive'] + '''</pre>
        </figure>
      </article>

      <article class="moment">
        <header class="moment-head">
          <h3><span class="no" aria-hidden="true">02</span> The flash</h3>
          <p class="caption">Under the v6 wall clock, nine seconds is the whole debate.</p>
        </header>
        <figure class="session" data-print aria-label="A flash crisis printed under the v6 wall clock, nine seconds on the clock">
          <span class="visually-hidden">The Vodka Shortage lists three options under the clock, which allows nine seconds. The answer is graded: order up 1, faith down 2.</span>
          <pre aria-hidden="true">''' + frag['vodka'] + '''</pre>
        </figure>
      </article>

      <article class="moment">
        <header class="moment-head">
          <h3><span class="no" aria-hidden="true">03</span> The dossier</h3>
          <p class="caption">Press d: the ledger of what you did, and the roads still shut.</p>
        </header>
        <figure class="session" data-print aria-label="The dossier listing the conditional roads still locked, the one available now">
          <span class="visually-hidden">Rails of History, mode Balanced. One road is available now; the rest stay locked behind years, thresholds, paths and earlier decisions.</span>
          <pre aria-hidden="true">''' + frag['dossier'] + '''</pre>
        </figure>
      </article>

    </div>
  </div>
</section>

<section class="yardstick">
  <div class="container">
    <header class="plan">
      <h2>Six ways to hold it</h2>
      <p class="lead">Six presets own the drift and the reserves. Four scenarios own the first year, and the last.</p>
    </header>
    <div class="deals">
      <div class="deal">
        <h3>The drift you accept</h3>
        <table>
          <thead>
            <tr><th scope="col">Preset</th><th scope="col">Doctrine</th><th scope="col">The deal</th></tr>
          </thead>
          <tbody>
            <tr><td class="flag">easy</td><td>SWEEPING REFORMS</td><td>Gentle drift, five reserves.</td></tr>
            <tr><td class="flag">medium</td><td>BALANCED</td><td>The historical grind, three reserves.</td></tr>
            <tr><td class="flag">hard</td><td>OLD GUARD IRON GRASP</td><td>Two reserves, and the system fights back.</td></tr>
            <tr><td class="flag">extreme</td><td>THE SYSTEM ITSELF</td><td>A single reserve. The Union is a rumour you must keep alive.</td></tr>
            <tr><td class="flag">flash</td><td>FLASH CRISIS</td><td>Nine seconds a decision, two reserves.</td></tr>
            <tr><td class="flag">historical</td><td>HISTORICAL RAILS</td><td>Real decline only. Divergence costs score.</td></tr>
          </tbody>
        </table>
      </div>
      <div class="deal">
        <h3>The year you inherit</h3>
        <table>
          <thead>
            <tr><th scope="col">Opening</th><th scope="col">Start</th><th scope="col">You inherit</th></tr>
          </thead>
          <tbody>
            <tr><td class="flag">rails</td><td>1964</td><td>History as it was left.</td></tr>
            <tr><td class="flag">reform</td><td>1964</td><td>Kosygin's profit memo, already won.</td></tr>
            <tr><td class="flag">flashpoint</td><td>1980</td><td>The 40th Army in the mountains, twelve years left.</td></tr>
            <tr><td class="flag">millennium</td><td>1992</td><td>The treaty held. Ten years stay red.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<section class="close">
  <div class="container">
    <header class="plan">
      <h2>In the tab or on the metal</h2>
      <p class="lead">The browser build is the same Python compiled to WebAssembly: about 12 MB on the first visit, then it runs offline. The desktop build needs Python 3.8 and nothing else.</p>
    </header>
    <div class="actions">
      <a class="btn" href="play/">Play in the browser</a>
    </div>
    <figure class="session" data-print aria-label="Three commands to install and run the game from source">
      <span class="visually-hidden">Clone the repository, enter the folder, run python main.py. On Windows use py main.py when python opens the store.</span>
      <pre aria-hidden="true">''' + frag['install'] + '''</pre>
    </figure>
    <p class="caption">On Windows, if <code>python</code> opens the store, run <code>py main.py</code>.</p>

    <article class="moment death">
      <header class="moment-head">
        <h3>The other exit</h3>
        <p class="caption">Any gauge at zero ends the year. The portraits take the rest.</p>
      </header>
      <figure class="session" data-print aria-label="The collapse screen of a 1979 failure">
        <span class="visually-hidden">Faith fell to zero in 1979 after fifteen governed years. Legacy score 133, with the line removed from the portraits.</span>
        <pre aria-hidden="true">''' + frag['death'] + '''</pre>
      </figure>
    </article>
  </div>
</section>

<footer class="colophon">
  <div class="container">
    <p class="wordmark">КРЕМЛЬ 1991</p>
    <nav class="nav-links" aria-label="Colophon">
      <a href="https://github.com/mahakammoonlightstudio-beep/kreml-1991">Source</a>
      <a href="https://github.com/mahakammoonlightstudio-beep/kreml-1991/releases">Releases</a>
      <a href="https://github.com/mahakammoonlightstudio-beep/kreml-1991/blob/master/LICENSE">MIT</a>
    </nav>
    <p class="fine">© 2026 Mahakam Moonlight Studio. The source is released under the MIT licence.</p>
  </div>
</footer>

</main>'''

t = t.replace(html_anchor, '</section>\n\n' + SECTIONS + '\n', 1)

# --- CSS for the new sections ---
css_anchor = '@media (min-width: 90rem) { .session pre { font-size: var(--text-xl); } }\n'
assert css_anchor in t, 'css anchor missing'
CSS = css_anchor + '''
/* below the fold: continuous terminal scroll, hairlines only */
.loop, .yardstick, .close { padding-block: var(--section-gap-s); }
.loop, .yardstick, .close, .colophon { border-top: var(--rule-hair) solid var(--color-rule); }
.plan { margin-block-end: var(--space-3xl); }
.plan .lead { margin-block-start: var(--space-md); }
.moments { display: grid; gap: var(--space-3xl); }
.moment-head { display: grid; gap: var(--space-2xs); margin-block-end: var(--space-md); }
.moment-head h3 { display: flex; align-items: baseline; gap: var(--space-xs); }
.moment-head .no { color: var(--color-accent); font-variant-numeric: tabular-nums; }
.caption { color: var(--color-muted); max-width: 62ch; }
.moment .session pre, .close .session pre { font-size: var(--text-md); line-height: 1.7; }
.session .alarm { color: var(--color-error); font-weight: 500; }
.deals { display: grid; gap: var(--space-lg); }
.deal { background: var(--color-paper-2); border: var(--rule-hair) solid var(--color-rule); padding: var(--space-lg) var(--space-xl); }
.deal table { width: 100%; border-collapse: collapse; margin-block-start: var(--space-md); font-size: var(--text-sm); font-variant-numeric: tabular-nums; }
.deal th, .deal td { padding: var(--space-xs) var(--space-md) var(--space-xs) 0; border-top: var(--rule-hair) solid var(--color-rule); text-align: left; vertical-align: top; font-weight: 400; line-height: 1.45; }
.deal thead th { color: var(--color-muted); font-size: var(--text-xs); letter-spacing: 0.08em; text-transform: uppercase; font-weight: 400; }
.deal td:nth-child(2) { font-weight: 500; letter-spacing: 0.02em; }
.deal td:nth-child(3) { color: var(--color-ink-2); }
.deal .flag { color: var(--color-muted); white-space: nowrap; }
.close .actions { display: flex; flex-wrap: wrap; gap: var(--space-sm); margin-block-end: var(--space-md); }
.close .actions .btn { min-width: 220px; justify-content: center; }
.close .session { margin-block: var(--space-lg); }
.close .death { margin-block-start: var(--space-3xl); }
.colophon { background: var(--color-paper-2); padding-block: var(--space-2xl); }
.colophon .container { display: flex; flex-wrap: wrap; align-items: baseline; gap: var(--space-sm) var(--space-2xl); }
.colophon .fine { margin-inline-start: auto; color: var(--color-muted); font-size: var(--text-sm); color: var(--color-muted); }
@media (min-width: 70rem) { .deals { grid-template-columns: 1fr 1fr; gap: var(--space-xl); } }
'''
t = t.replace(css_anchor, CSS, 1)

open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('spliced; new size', len(t), 'chars')
