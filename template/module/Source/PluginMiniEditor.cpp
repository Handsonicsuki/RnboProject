#include "PluginMiniEditor.h"

#include "PluginProcessor.h"
#include "ssp/controls/MiniControl.h"

using pcontrol_type = ssp::MiniControl;
using bcontrol_type = ssp::ParamButton;

PluginMiniEditor::PluginMiniEditor(PluginProcessor &p) : base_type(&p), processor_(p) {
    auto view = std::make_shared<ssp::MiniParamView>(&p);

    for (const auto &param : processor_.params_.rnboParams_) {
        float inc = 1.0f;
        float finc = 0.01f;
        if (param->enumValues_) {
            finc = inc;
        } else if (param->steps_ > 2) {
            inc = (param->max_ - param->min_) / (param->steps_ - 1);
            finc = inc;
        }

        view->addParam(std::make_shared<pcontrol_type>(param->val_, inc, finc));
    }

    addView(view);
    setView(0);
}
