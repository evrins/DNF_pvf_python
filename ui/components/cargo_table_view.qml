import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Column {
    id: root

    property var headerLabels: ["#", "Name", "Num", "Id", "Rarity"]
    property int hoveredRow: -1
    property int selectedRow: -1
    property var tableModel

    // Signal for external components to listen to selection changes
    signal rowSelected(int row)

    // Column width function used by both header and table
    function getColumnWidth(column) {
        switch (column) {
        case 0:
            return 48;
        case 1:
            return 240;
        case 2:
            return 48;
        case 3:
            return 80;
        default:
            return 72;
        }
    }

    onSelectedRowChanged: {
        if (selectedRow >= 0) {
            rowSelected(selectedRow);
        }
    }

    // Header using HorizontalHeaderView
    HorizontalHeaderView {
        id: horizontalHeader

        height: 32
        model: headerLabels
        syncView: tableView
        width: parent.width

        delegate: Rectangle {
            implicitHeight: 32
            implicitWidth: getColumnWidth(index)
            border.color: "#d1d5db"
            border.width: 1
            color: "#f3f4f6"

            Text {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignLeft
                color: "#374151"
                font.bold: true
                font.pixelSize: 13
                text: modelData
                elide: Text.ElideRight
            }
        }
    }
    TableView {
        id: tableView

        boundsBehavior: Flickable.StopAtBounds

        // Table styling
        clip: true
        
        // Disable dragging/flicking
        interactive: true
        flickableDirection: Flickable.AutoFlickDirection

        // Column widths
        columnWidthProvider: function (column) {
            return getColumnWidth(column);
        }
        height: parent.height - horizontalHeader.height
        model: tableModel

        // Enable selection
        selectionBehavior: TableView.SelectRows
        selectionMode: TableView.SingleSelection
        width: parent.width

        // Delegate for each cell with selection support
        delegate: Rectangle {
            id: cellDelegate

            border.color: "#e5e7eb"
            border.width: 0.5

            // Modern color scheme with better contrast
            color: {
                if (root.selectedRow === model.row) {
                    return "#2563eb";  // Modern blue for selection
                } else if (root.hoveredRow === model.row) {
                    return '#e3f2fd';
                } else if (model.row % 2 === 0) {
                    return "#f9fafb";  // Light gray for alternating rows
                } else {
                    return "#ffffff";  // White for odd rows
                }
            }
            implicitHeight: 35

            Text {
                anchors.left: parent.left
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                color: {
                    if (root.selectedRow === model.row) {
                        return "#ffffff";  // White text on selected row
                    } else {
                        return "#374151";  // Dark gray for better readability
                    }
                }
                elide: Text.ElideRight
                font.pixelSize: 13
                text: model.display || ""
                width: parent.width - 16  // Account for left and right margins
            }

            // Mouse area for row selection
            MouseArea {
                anchors.fill: parent

                // Enhanced visual feedback on hover
                hoverEnabled: true

                onClicked: {
                    if (root.selectedRow === model.row) {
                        root.selectedRow = -1;
                        console.log('unselected row');
                    } else {
                        root.selectedRow = model.row;
                    }
                    console.log("Selected row:", model.row, "Data:", model.display);
                }
                onEntered: {
                    root.hoveredRow = model.row;
                }
                onExited: {
                    root.hoveredRow = -1;
                }
            }
        }
    }
}
