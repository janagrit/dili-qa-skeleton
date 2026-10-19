
const Table = require("cli-table3")
const env = process.env

let chalk

;(async () => {
  const chalkModule = await import("chalk")
  chalk = new chalkModule.Chalk({ level: 3 })
})()


class TableSummaryReporter {
  constructor() {
    this.testResults = {}
    this.finalResults = new Map()
    this.summary = { passed: 0, failed: 0, skipped: 0 }
  }

  onTestEnd(test, result) {
    if (!chalk) {
      // fallback if chalk not loaded yet
      chalk = { green: s => s, red: s => s, yellow: s => s, cyan: s => s, magenta: s => s, blue: s => s, bold: s => s }
    }

    const section = test.parent?.title || "Unknown Suite"
    if (!this.testResults[section]) this.testResults[section] = []

    const status =
      result.status === "passed"
        ? chalk.green("Passed")
        : result.status === "failed"
        ? chalk.red("Failed")
        : chalk.yellow("Skipped")

    const duration = result.duration
      ? this.formatDuration(result.duration)
      : "N/A"
    const testKey = `${section}::${test.title}`

    if (result.status === "passed") {
      this.finalResults.set(testKey, {
        suite: section,
        name: test.title,
        status,
        duration,
      })
      if (
        !this.testResults[testKey] ||
        this.testResults[testKey] !== "passed"
      ) {
        this.summary.passed++
      }
    } else if (!this.finalResults.has(testKey)) {
      this.finalResults.set(testKey, {
        suite: section,
        name: test.title,
        status,
        duration,
      })
      if (result.status === "failed") this.summary.failed++
      if (result.status === "skipped") this.summary.skipped++
    }

    this.testResults[section].push({ name: test.title, status, duration })
  }

  formatDuration(ms) {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return minutes > 0 ? `${minutes}m ${remainingSeconds}s` : `${seconds}s`
  }

  onEnd() {
    if (!chalk) {
      // fallback if chalk not loaded yet
      chalk = { green: s => s, red: s => s, yellow: s => s, cyan: s => s, magenta: s => s, blue: s => s, bold: s => s }
    }

    const environment = env.environment || env.ENVIRONMENT || env.NEXT_PUBLIC_ENV || 'unknown'
    const misCode = env.PLAYWRIGHT_MisCode || env.misCode || env.NEXT_PUBLIC_MISCODE || 'n/a'


    console.log(
      chalk.bold(
        `\nRunning Environment: ${chalk.cyan(environment.toUpperCase())}`
      )
    )
    // console.log(chalk.bold(`MIS Code: ${chalk.magenta(misCode)}`))

    console.log(chalk.bold("\nFinal Summary for All Sections:\n"))

    if (!this.finalResults || this.finalResults.size === 0) {
      console.log(chalk.yellow("No test results recorded."))
      return
    }

    for (const section of Object.keys(this.testResults)) {
      this.printSectionSummary(section)
    }

    console.log(
      chalk.bold(
        "\n ========================================================================================"
      )
    )


    const tableFinal = new Table({
      head: ["Test Suite", "Test Name", "Status", "Duration"],
      colWidths: [30, 60, 8, 7],
    })

    ;[...this.finalResults.values()].forEach(res => {
      tableFinal.push([res.suite, res.name, res.status, res.duration])
    })

    console.log(tableFinal.toString())

    console.log(`\nTotal Tests: ${this.finalResults.size}`)
    console.log(chalk.green(`Passed: ${this.summary.passed}`))
    console.log(chalk.red(`Failed: ${this.summary.failed}`))
    console.log(chalk.yellow(`Skipped: ${this.summary.skipped}`))
  }

  printSectionSummary(section) {
    const table = new Table({
      head: ["Test Name", "Status", "Duration"],
      colWidths: [70, 10, 10],
    })

    const results = this.testResults[section]
    results.forEach(res => {
      table.push([res.name, res.status, res.duration])
    })

    console.log(chalk.blue.bold(`\n${section} Section Summary:`))
    console.log(table.toString())
  }
}

module.exports = TableSummaryReporter
