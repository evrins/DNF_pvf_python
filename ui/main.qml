import QtQuick 6.10
import QtQuick.Controls 6.10
import QtQuick.Layouts 6.10

import "./components" as Components

ApplicationWindow {
    id: window

    property string currTime: '00:00:00'

    // Note: cargoModel is provided by the Python backend via context property

    height: 600
    title: "Clock"
    visible: true
    width: 800

    // Check if backend is available
    Component.onCompleted: {
        if (typeof backend !== 'undefined') {
            console.log("Backend is available");
            if (backend.isReady()) {
                console.log("Backend is ready");
            }
        } else {
            console.log("Error: Backend is not defined!");
        }
    }

    Connections {
        function onUpdated(msg) {
            currTime = msg;
        }

        target: typeof backend !== 'undefined' ? backend : null
    }
    // Main layout using Column
    Column {
        anchors.fill: parent

        TabBar {
            id: bar

            width: parent.width

            TabButton {
                text: qsTr("Home")
            }
            TabButton {
                text: qsTr("Discover")
            }
            TabButton {
                text: qsTr("Activity")
            }
            TabButton {
                text: "Cargo"
            }
        }
        StackLayout {
            id: stackLayout

            currentIndex: bar.currentIndex
            height: parent.height - bar.height
            width: parent.width

            // Home Tab Content
            Item {
                id: homeTab

                Rectangle {
                    anchors.fill: parent

                    Image {
                        anchors.fill: parent
                        fillMode: Image.PreserveAspectCrop
                        source: "./images/background.png"
                    }
                    Rectangle {
                        anchors.fill: parent
                        color: "transparent"

                        Text {
                            color: 'white'
                            font.pixelSize: 48
                            text: currTime

                            anchors {
                                bottom: parent.bottom
                                bottomMargin: 12
                                left: parent.left
                                leftMargin: 12
                            }
                        }
                        Button {

                            enabled: typeof backend !== 'undefined'
                            text: 'Click me'

                            onClicked: {
                                if (typeof backend !== 'undefined') {
                                    backend.on_button_clicked();
                                } else {
                                    console.log("Backend not available");
                                }
                            }

                            anchors {
                                centerIn: parent
                            }
                        }
                    }
                }
            }

            // Discover Tab Content
            Item {
                id: discoverTab

                Rectangle {
                    anchors.fill: parent
                    color: "#f0f0f0"

                    Text {
                        anchors.centerIn: parent
                        color: "#333"
                        font.pixelSize: 24
                        text: "Discover Content"
                    }
                }
            }

            // Activity Tab Content
            Item {
                id: activityTab

                Rectangle {
                    anchors.fill: parent
                    color: "#e8f4f8"

                    Text {
                        anchors.centerIn: parent
                        color: "#333333"
                        font {
                            pixelSize: 24
                            family: "Arial, sans-serif"
                        }
                        text: "Activity Content"
                    }
                }
            }

            Item {
                id: cargoTab

                Rectangle {
                    anchors.fill: parent
                    color: "#f8f8f8"

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10

                        Text {
                            text: "Cargo Inventory"
                            font.pixelSize: 20
                            font.bold: true
                            color: "#333"
                        }

                        // Use the cargo table view component
                        Loader {
                            id: cargoTableLoader
                            width: parent.width
                            height: parent.height - 80
                            source: "./components/cargo_table_view.qml"

                            onLoaded: {
                                if (item) {
                                    item.tableModel = cargoModel;
                                    // Connect to selection signal
                                    item.rowSelected.connect(function (row) {
                                        selectedItemText.text = "Selected: Row " + row;
                                    });
                                }
                            }
                        }

                        // Selection feedback
                        Text {
                            id: selectedItemText
                            text: "No item selected"
                            font.pixelSize: 14
                            color: "#666"
                            height: 30
                        }
                    }
                }
            }
        }
    }
}
