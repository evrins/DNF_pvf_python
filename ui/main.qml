import QtQuick 6.10
import QtQuick.Controls 6.10
import QtQuick.Layouts 6.10

ApplicationWindow {
    id: window

    property string currTime: '00:00:00'

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
                        color: '#333'
                        font.pixelSize: 24
                        text: "Activity Content"
                    }
                }
            }
        }
    }
}