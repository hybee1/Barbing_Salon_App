/* ==========================================================
   salon-manager-reports.js
   Levelz Cuts - Manager Reports
========================================================== */


let reportsInitialized = false;

let currentReport = null;


/* ==========================================================
   INITIALIZE
========================================================== */

function initReportsPage() {

    if (reportsInitialized) {

        loadReports();

        return;

    }

    reportsInitialized = true;

    setupReportFilters();

    setDefaultReportDates();

    loadReports();

}


/* ==========================================================
   SETUP FILTERS
========================================================== */

function setupReportFilters() {

    const form =
        document.getElementById(
            "reportFilterForm"
        );

    if (!form) return;

    form.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();

            loadReports();

        }
    );


    const clearButton =
        document.getElementById(
            "clearReportFilters"
        );

    if (clearButton) {

        clearButton.addEventListener(
            "click",
            function () {

                setDefaultReportDates();

                loadReports();

            }
        );

    }

}


/* ==========================================================
   DEFAULT DATES
========================================================== */

function setDefaultReportDates() {

    const startInput =
        document.getElementById(
            "reportStartDate"
        );

    const endInput =
        document.getElementById(
            "reportEndDate"
        );

    if (!startInput || !endInput) return;


    const today =
        new Date();


    const formatted =
        formatDateForInput(
            today
        );


    startInput.value =
        formatted;

    endInput.value =
        formatted;


    endInput.min =
        formatted;

}


/* ==========================================================
   LOAD REPORTS
========================================================== */

async function loadReports() {

    const container =
        document.getElementById(
            "reportsContainer"
        );

    if (!container) return;


    const startInput =
        document.getElementById(
            "reportStartDate"
        );

    const endInput =
        document.getElementById(
            "reportEndDate"
        );


    let startDate =
        startInput?.value || "";

    let endDate =
        endInput?.value || "";


    if (!startDate || !endDate) {

        setDefaultReportDates();

        startDate =
            startInput?.value || "";

        endDate =
            endInput?.value || "";

    }


    if (startDate > endDate) {

        showReportError(
            "Start date cannot be after end date."
        );

        return;

    }


    showReportsLoading();


    try {

        const query =
            new URLSearchParams({

                start_date: startDate,

                end_date: endDate,

            });


        const data =
            await apiRequest(
                `/reports/range/?${query.toString()}`
            );


        currentReport =
            data;


        renderReports(
            data
        );


    } catch (error) {

        console.error(
            "Failed to load reports:",
            error
        );


        showReportError(
            "Unable to load reports. Please try again."
        );

    }

}


/* ==========================================================
   LOADING
========================================================== */

function showReportsLoading() {

    const container =
        document.getElementById(
            "reportsContainer"
        );

    if (!container) return;


    container.innerHTML = `

        <div class="card reports-loading-card">

            <div class="reports-loading">

                <i class="fa-solid fa-chart-line"></i>

                <p>
                    Loading report...
                </p>

            </div>

        </div>

    `;

}


/* ==========================================================
   ERROR
========================================================== */

function showReportError(message) {

    const container =
        document.getElementById(
            "reportsContainer"
        );

    if (!container) return;


    container.innerHTML = `

        <div class="card">

            <div class="report-error">

                <i class="fa-solid fa-circle-exclamation"></i>

                <span>
                    ${escapeReportHtml(message)}
                </span>

            </div>

        </div>

    `;

}


/* ==========================================================
   RENDER REPORT
========================================================== */

function renderReports(data) {

    const container =
        document.getElementById(
            "reportsContainer"
        );

    if (!container) return;


    const bookings =
        data.bookings || {};


    const revenue =
        data.revenue || {};


    const services =
        data.services || [];


    const staff =
        data.staff || [];


    const trend =
        data.trend || [];


    const completionRate =
        Number(
            data.completion_rate || 0
        );


    const startDate =
        data.start_date || "";


    const endDate =
        data.end_date || "";


    const grouping =
        data.grouping || "day";


    container.innerHTML = `

        <!-- ==================================================
             REPORT FILTER
        =================================================== -->

        <section class="card reports-filter-card">

            <div class="reports-filter-header">

                <div>

                    <h2>
                        Report Period
                    </h2>

                    <p>
                        Select the period you want to analyse.
                    </p>

                </div>

                <span class="report-range-label">

                    <i class="fa-solid fa-calendar-days"></i>

                    ${formatReportDateRange(
                        startDate,
                        endDate
                    )}

                </span>

            </div>


            <form
                id="reportFilterForm"
                class="reports-filter-form"
            >

                <div class="reports-date-group">

                    <label for="reportStartDate">
                        Start Date
                    </label>

                    <input
                        type="date"
                        id="reportStartDate"
                        value="${escapeReportAttribute(
                            startDate
                        )}"
                    >

                </div>


                <div class="reports-date-group">

                    <label for="reportEndDate">
                        End Date
                    </label>

                    <input
                        type="date"
                        id="reportEndDate"
                        value="${escapeReportAttribute(
                            endDate
                        )}"
                    >

                </div>


                <div class="reports-filter-actions">

                    <button
                        type="submit"
                        class="gold-btn"
                    >

                        <i class="fa-solid fa-chart-line"></i>

                        Generate Report

                    </button>


                    <button
                        type="button"
                        class="gold-btn"
                        id="clearReportFilters"
                    >

                        Clear

                    </button>

                </div>

            </form>

        </section>


        <!-- ==================================================
             SUMMARY
        =================================================== -->

        <section class="report-summary-grid">

            <article class="report-stat-card">

                <div class="report-stat-content">

                    <small>
                        Total Bookings
                    </small>

                    <h2>
                        ${bookings.total ?? 0}
                    </h2>

                    <p>
                        All bookings in period
                    </p>

                </div>

                <div class="report-stat-icon">

                    <i class="fa-solid fa-calendar-check"></i>

                </div>

            </article>


            <article class="report-stat-card">

                <div class="report-stat-content">

                    <small>
                        Completed
                    </small>

                    <h2>
                        ${bookings.completed ?? 0}
                    </h2>

                    <p>
                        Completed bookings
                    </p>

                </div>

                <div class="report-stat-icon">

                    <i class="fa-solid fa-circle-check"></i>

                </div>

            </article>


            <article class="report-stat-card">

                <div class="report-stat-content">

                    <small>
                        Revenue
                    </small>

                    <h2>
                        ${formatReportMoney(
                            revenue.total
                        )}
                    </h2>

                    <p>
                        Completed bookings
                    </p>

                </div>

                <div class="report-stat-icon">

                    <i class="fa-solid fa-naira-sign"></i>

                </div>

            </article>


            <article class="report-stat-card">

                <div class="report-stat-content">

                    <small>
                        Completion Rate
                    </small>

                    <h2>
                        ${formatReportPercent(
                            completionRate
                        )}
                    </h2>

                    <p>
                        Completed ÷ total bookings
                    </p>

                </div>

                <div class="report-stat-icon">

                    <i class="fa-solid fa-chart-pie"></i>

                </div>

            </article>

        </section>


        <!-- ==================================================
             TREND + STATUS
        =================================================== -->

        <section class="reports-main-grid">


            <!-- TREND -->

            <section class="card">

                <div class="report-card-header">

                    <div>

                        <h2>
                            Performance Trend
                        </h2>

                        <p>
                            ${getGroupingDescription(
                                grouping
                            )}
                        </p>

                    </div>


                    <div class="report-chart-legend">

                        <span class="report-chart-legend-dot"></span>

                        Revenue

                    </div>

                </div>


                <div class="report-chart-wrapper">

                    ${renderRevenueChart(
                        trend
                    )}

                </div>

            </section>


            <!-- STATUS -->

            <section class="card">

                <div class="report-card-header">

                    <div>

                        <h2>
                            Booking Status
                        </h2>

                        <p>
                            Booking distribution
                        </p>

                    </div>

                </div>


                ${renderStatusReport(
                    bookings
                )}

            </section>

        </section>


        <!-- ==================================================
             PERIOD BREAKDOWN
        =================================================== -->

        <section class="card report-table-card">

            <div class="report-card-header">

                <div>

                    <h2>
                        ${getGroupingTitle(
                            grouping
                        )} Breakdown
                    </h2>

                    <p>
                        Booking and revenue performance
                        throughout the selected period.
                    </p>

                </div>

            </div>


            <div class="report-table-container">

                <table>

                    <thead>

                        <tr>

                            <th>
                                ${getPeriodColumnTitle(
                                    grouping
                                )}
                            </th>

                            <th>
                                Bookings
                            </th>

                            <th>
                                Completed
                            </th>

                            <th>
                                Revenue
                            </th>

                            <th>
                                Completion
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        ${
                            trend.length
                            ? trend.map(
                                renderTrendRow
                            ).join("")
                            : `
                                <tr>

                                    <td
                                        colspan="5"
                                        class="report-empty-state"
                                    >

                                        No report data
                                        available.

                                    </td>

                                </tr>
                            `
                        }

                    </tbody>

                </table>

            </div>

        </section>


        <!-- ==================================================
             SERVICES + STAFF
        =================================================== -->

        <section class="report-lower-grid">


            <!-- SERVICES -->

            <section class="card">

                <div class="report-card-header">

                    <div>

                        <h2>
                            Top Services
                        </h2>

                        <p>
                            Services generating the most
                            completed bookings.
                        </p>

                    </div>

                </div>


                <div class="report-table-container">

                    <table>

                        <thead>

                            <tr>

                                <th>
                                    Service
                                </th>

                                <th>
                                    Bookings
                                </th>

                                <th>
                                    Revenue
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            ${
                                services.length
                                ? services.map(
                                    service => `

                                        <tr>

                                            <td>

                                                ${escapeReportHtml(
                                                    service.service__name ||
                                                    "Unknown Service"
                                                )}

                                            </td>


                                            <td>

                                                ${
                                                    service.booking_count ??
                                                    0
                                                }

                                            </td>


                                            <td class="report-revenue">

                                                ${formatReportMoney(
                                                    service.revenue
                                                )}

                                            </td>

                                        </tr>

                                    `
                                ).join("")
                                : `

                                    <tr>

                                        <td
                                            colspan="3"
                                            class="report-empty-state"
                                        >

                                            No completed bookings.

                                        </td>

                                    </tr>

                                `
                            }

                        </tbody>

                    </table>

                </div>

            </section>


            <!-- STAFF -->

            <section class="card">

                <div class="report-card-header">

                    <div>

                        <h2>
                            Staff Performance
                        </h2>

                        <p>
                            Performance across the
                            selected period.
                        </p>

                    </div>

                </div>


                <div class="report-table-container">

                    <table>

                        <thead>

                            <tr>

                                <th>
                                    Staff
                                </th>

                                <th>
                                    Bookings
                                </th>

                                <th>
                                    Revenue
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            ${
                                staff.length
                                ? staff.map(
                                    member => `

                                        <tr>

                                            <td>

                                                ${escapeReportHtml(
                                                    member.staff_name ||
                                                    "Unknown Staff"
                                                )}

                                            </td>


                                            <td>

                                                ${
                                                    member.booking_count ??
                                                    0
                                                }

                                            </td>


                                            <td class="report-revenue">

                                                ${formatReportMoney(
                                                    member.revenue
                                                )}

                                            </td>

                                        </tr>

                                    `
                                ).join("")
                                : `

                                    <tr>

                                        <td
                                            colspan="3"
                                            class="report-empty-state"
                                        >

                                            No completed bookings.

                                        </td>

                                    </tr>

                                `
                            }

                        </tbody>

                    </table>

                </div>

            </section>

        </section>

    `;


    setupReportFilters();

    syncReportDateConstraints();

}


/* ==========================================================
   STATUS REPORT
========================================================== */

function renderStatusReport(bookings) {

    const statuses = [

        {
            key: "confirmed",
            label: "Confirmed"
        },

        {
            key: "arrived",
            label: "Arrived"
        },

        {
            key: "in_progress",
            label: "In Progress"
        },

        {
            key: "completed",
            label: "Completed"
        },

        {
            key: "cancelled",
            label: "Cancelled"
        },

        {
            key: "no_show",
            label: "No Show"
        }

    ];


    const total =
        Number(
            bookings.total || 0
        );


    return `

        <div class="report-status-list">

            ${
                statuses.map(
                    status => {

                        const value =
                            Number(
                                bookings[
                                    status.key
                                ] || 0
                            );


                        const percentage =
                            total > 0
                            ? (
                                value /
                                total
                            ) * 100
                            : 0;


                        return `

                            <div class="report-status-item">

                                <div class="report-status-top">

                                    <span class="report-status-name">

                                        ${status.label}

                                    </span>


                                    <span class="report-status-value">

                                        ${value}

                                    </span>

                                </div>


                                <div class="report-status-bar">

                                    <div
                                        class="report-status-fill"
                                        style="width:${percentage}%"
                                    ></div>

                                </div>

                            </div>

                        `;

                    }
                ).join("")
            }

        </div>

    `;

}


/* ==========================================================
   REVENUE CHART
========================================================== */

function renderRevenueChart(trend) {

    if (!trend.length) {

        return `

            <div class="report-chart-empty">

                <div>

                    <i class="fa-solid fa-chart-line"></i>

                    <p>
                        No revenue data available.
                    </p>

                </div>

            </div>

        `;

    }


    const width = 760;

    const height = 300;

    const paddingLeft = 55;

    const paddingRight = 25;

    const paddingTop = 25;

    const paddingBottom = 45;


    const chartWidth =
        width -
        paddingLeft -
        paddingRight;


    const chartHeight =
        height -
        paddingTop -
        paddingBottom;


    const revenues =
        trend.map(
            item =>
                Number(
                    item.revenue || 0
                )
        );


    const maxRevenue =
        Math.max(
            ...revenues,
            1
        );


    const points =
        trend.map(
            (item, index) => {

                const x =
                    trend.length === 1
                    ? paddingLeft +
                      chartWidth / 2
                    : paddingLeft +
                      (
                          index /
                          (trend.length - 1)
                      ) *
                      chartWidth;


                const revenue =
                    Number(
                        item.revenue || 0
                    );


                const y =
                    paddingTop +
                    chartHeight -
                    (
                        revenue /
                        maxRevenue
                    ) *
                    chartHeight;


                return {
                    x,
                    y,
                    revenue,
                    item
                };

            }
        );


    const linePath =
        points.map(
            (point, index) => {

                return `${
                    index === 0
                    ? "M"
                    : "L"
                } ${point.x} ${point.y}`;

            }
        ).join(" ");


    const areaPath = `

        ${linePath}

        L ${points[points.length - 1].x}
          ${paddingTop + chartHeight}

        L ${points[0].x}
          ${paddingTop + chartHeight}

        Z

    `;


    const gridLines =
        [0, 25, 50, 75, 100].map(
            percentage => {

                const y =
                    paddingTop +
                    chartHeight -
                    (
                        percentage /
                        100
                    ) *
                    chartHeight;


                const value =
                    (
                        maxRevenue *
                        percentage /
                        100
                    );


                return `

                    <line
                        x1="${paddingLeft}"
                        y1="${y}"
                        x2="${width - paddingRight}"
                        y2="${y}"
                        class="report-chart-grid-line"
                    />

                    <text
                        x="${paddingLeft - 10}"
                        y="${y + 4}"
                        text-anchor="end"
                        class="report-chart-axis-label"
                    >
                        ${formatCompactMoney(value)}
                    </text>

                `;

            }
        ).join("");


    const labels =
        points.map(
            (point, index) => {

                if (
                    trend.length > 12 &&
                    index % Math.ceil(
                        trend.length / 8
                    ) !== 0 &&
                    index !== trend.length - 1
                ) {

                    return "";

                }


                return `

                    <text
                        x="${point.x}"
                        y="${height - 15}"
                        text-anchor="middle"
                        class="report-chart-axis-label"
                    >
                        ${escapeReportHtml(
                            point.item.period_label ||
                            point.item.period ||
                            ""
                        )}
                    </text>

                `;

            }
        ).join("");


    const circles =
        points.map(
            point => `

                <circle
                    cx="${point.x}"
                    cy="${point.y}"
                    r="5"
                    class="report-chart-point"
                >

                    <title>
                        ${escapeReportHtml(
                            point.item.period_label ||
                            point.item.period ||
                            ""
                        )}
                        :
                        ${formatReportMoney(
                            point.revenue
                        )}
                    </title>

                </circle>

            `
        ).join("");


    return `

        <svg
            class="report-chart"
            viewBox="0 0 ${width} ${height}"
            preserveAspectRatio="none"
            role="img"
            aria-label="Revenue trend chart"
        >

            <defs>

                <linearGradient
                    id="reportGoldGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                >

                    <stop
                        offset="0%"
                        stop-color="#C89B3C"
                    />

                    <stop
                        offset="100%"
                        stop-color="#C89B3C"
                        stop-opacity="0"
                    />

                </linearGradient>

            </defs>


            ${gridLines}


            <path
                d="${areaPath}"
                class="report-chart-area"
            />


            <path
                d="${linePath}"
                class="report-chart-line"
            />


            ${circles}


            ${labels}

        </svg>

    `;

}


/* ==========================================================
   TREND ROW
========================================================== */

function renderTrendRow(item) {

    return `

        <tr>

            <td class="report-period">

                ${escapeReportHtml(
                    item.period_label ||
                    item.period ||
                    "-"
                )}

            </td>


            <td>

                ${item.bookings ?? 0}

            </td>


            <td>

                ${item.completed ?? 0}

            </td>


            <td class="report-revenue">

                ${formatReportMoney(
                    item.revenue
                )}

            </td>


            <td class="report-completion">

                ${formatReportPercent(
                    item.completion_rate
                )}

            </td>

        </tr>

    `;

}


/* ==========================================================
   GROUPING HELPERS
========================================================== */

function getGroupingTitle(grouping) {

    if (grouping === "month") {

        return "Monthly";

    }


    if (grouping === "week") {

        return "Weekly";

    }


    return "Daily";

}


function getPeriodColumnTitle(grouping) {

    if (grouping === "month") {

        return "Month";

    }


    if (grouping === "week") {

        return "Week";

    }


    return "Day";

}


function getGroupingDescription(grouping) {

    if (grouping === "month") {

        return "Revenue grouped by month.";

    }


    if (grouping === "week") {

        return "Revenue grouped by week.";

    }


    return "Revenue grouped by day.";

}


/* ==========================================================
   DATE HELPERS
========================================================== */

function formatDateForInput(date) {

    const year =
        date.getFullYear();


    const month =
        String(
            date.getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const day =
        String(
            date.getDate()
        ).padStart(
            2,
            "0"
        );


    return `${year}-${month}-${day}`;

}


function formatReportDateRange(
    startDate,
    endDate
) {

    if (!startDate || !endDate) {

        return "Select period";

    }


    const start =
        parseReportDate(
            startDate
        );


    const end =
        parseReportDate(
            endDate
        );


    if (!start || !end) {

        return `${startDate} - ${endDate}`;

    }


    const options = {

        day: "numeric",

        month: "short",

        year: "numeric"

    };


    return `${start.toLocaleDateString(
        "en-NG",
        options
    )} - ${end.toLocaleDateString(
        "en-NG",
        options
    )}`;

}


function parseReportDate(value) {

    if (!value) return null;


    const parts =
        value.split("-");


    if (parts.length !== 3) {

        return null;

    }


    return new Date(
        Number(parts[0]),
        Number(parts[1]) - 1,
        Number(parts[2])
    );

}


/* ==========================================================
   DATE CONSTRAINTS
========================================================== */

function syncReportDateConstraints() {

    const startInput =
        document.getElementById(
            "reportStartDate"
        );


    const endInput =
        document.getElementById(
            "reportEndDate"
        );


    if (!startInput || !endInput) {

        return;

    }


    endInput.min =
        startInput.value;


    startInput.addEventListener(
        "change",
        function () {

            endInput.min =
                startInput.value;


            if (
                endInput.value &&
                endInput.value <
                startInput.value
            ) {

                endInput.value =
                    startInput.value;

            }

        }
    );

}


/* ==========================================================
   MONEY
========================================================== */

function formatReportMoney(value) {

    return `₦${Number(
        value || 0
    ).toLocaleString(
        "en-NG",
        {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    )}`;

}


function formatCompactMoney(value) {

    const amount =
        Number(
            value || 0
        );


    if (amount >= 1000000) {

        return `₦${(
            amount / 1000000
        ).toFixed(1)}m`;

    }


    if (amount >= 1000) {

        return `₦${(
            amount / 1000
        ).toFixed(0)}k`;

    }


    return `₦${Math.round(
        amount
    )}`;

}


function formatReportPercent(value) {

    return `${Number(
        value || 0
    ).toFixed(1)}%`;

}


/* ==========================================================
   HTML ESCAPING
========================================================== */

function escapeReportHtml(value) {

    return String(
        value ?? ""
    )
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}


function escapeReportAttribute(value) {

    return escapeReportHtml(
        value
    );

}
