package com.zorkvdo.app

import io.flutter.app.FlutterApplication
import io.flutter.plugin.common.PluginRegistry
import io.flutter.plugins.firebase.crashlytics.FlutterErrorReporter
import io.flutter.view.FlutterMain

class ZorkVDOApplication : FlutterApplication() {
    override fun onCreate() {
        super.onCreate()
        FlutterMain.startInitialization(this)
        // Firebase Crashlytics is auto-initialised via the SDK
    }
}
