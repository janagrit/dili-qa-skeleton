// Playwright reporter: prints a single result table at the end of every run.
// Wired in via playwright.config.ts (`reporter`). Distinguishes genuine
// failures from expected `test.fail` known-bug tests so the summary is honest.

const Table = require("cli-table3")

class TableSummaryReporter {
  constructor() {
    // Keyed by test id so retries collapse to the final attempt.
    this.results = new Map()
  }

  onTestEnd(test, result) {
    this.results.set(test.id, {
      suite: test.parent?.title || "Unknown Suite",
      name: test.title,
      key: this._classify(test, result),
      duration: this._formatDuration(result.duration),
    })
  }

  _classify(test, result) {
    // outcome(): 'skipped' | 'expected' | 'unexpected' | 'flaky'
    const outcome = typeof test.outcome === "function" ? test.outcome() : "expected"
    if (result.status === "skipped" || outcome === "skipped") return "skipped"
    // Expected failure = a `test.fail` known-bug test that failed as intended.
    if (outcome === "expected" && result.status !== "passed") return "knownbug"
    // Unexpected = genuine failure, incl. a `test.fail` test that now PASSES
    // (bug fixed → remove the marker).
    if (outcome === "unexpected" || result.status === "failed" || result.status === "timedOut") {
      return "failed"
    }
    if (outcome === "flaky") return "flaky"
    return "passed"
  }

  _formatDuration(ms) {
    if (!ms) return "0s"
    const seconds = Math.round(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    return minutes > 0 ? `${minutes}m ${seconds % 60}s` : `${seconds}s`
  }

  async onEnd() {
    let chalk
    try {
      const mod = await import("chalk")
      chalk = new mod.Chalk({ level: 3 })
    } catch {
      const identity = (s) => s
      chalk = { green: identity, red: identity, yellow: identity, cyan: identity, magenta: identity, bold: identity }
    }

    const labels = {
      passed: chalk.green("Passed"),
      failed: chalk.red("Failed"),
      knownbug: chalk.cyan("Known bug"),
      skipped: chalk.yellow("Skipped"),
      flaky: chalk.magenta("Flaky"),
    }

    const rows = [...this.results.values()]
    if (rows.length === 0) {
      console.log(chalk.yellow("\nNo test results recorded."))
      return
    }

    const table = new Table({
      head: ["Test Suite", "Test Name", "Status", "Duration"],
      colWidths: [26, 56, 11, 10],
      wordWrap: true,
    })
    for (const r of rows) table.push([r.suite, r.name, labels[r.key], r.duration])
    console.log("\n" + table.toString())

    const count = (key) => rows.filter((r) => r.key === key).length
    console.log(chalk.bold(`\nTotal: ${rows.length}`))
    console.log(chalk.green(`Passed: ${count("passed")}`))
    console.log(chalk.red(`Failed: ${count("failed")}`))
    console.log(chalk.cyan(`Known bugs (expected fail): ${count("knownbug")}`))
    if (count("flaky")) console.log(chalk.magenta(`Flaky: ${count("flaky")}`))
    console.log(chalk.yellow(`Skipped: ${count("skipped")}`))
  }
}

module.exports = TableSummaryReporter
