/*
    Launcher for pilatus-synthesizer embeddable distribution.

    Build in a Visual Studio Tools command prompt:

        cl /D WINDOWS /D UNICODE /MT /EHsc run.cpp

    Optionally set an icon (requires rcedit):

        rcedit\rcedit-x64.exe synthesizer.exe --set-icon path\to\synthesizer.ico

    The resulting synthesizer.exe should sit at the root of the distribution
    folder, alongside the embeddables\ folder and build\synthesizer.py.
*/

#include <windows.h>
#include <string>
#pragma comment(lib, "shlwapi")
#include <shlwapi.h>    // for PathFileExists
#pragma comment(lib, "user32.lib")

std::wstring SCRIPT_PATH(L"build\\synthesizer.py");

void check_existence(const std::wstring path)
{
    if (!PathFileExists(path.c_str()))
    {
        std::wstring message = path + L"  does not exist.";
        MessageBox(NULL, message.c_str(), L"Resource Error", MB_OK | MB_ICONERROR);
        exit(-1);
    }
}

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE, PWSTR pCmdLine, int nCmdShow)
{
    std::wstring emb_folder(L".\\embeddables");

    check_existence(emb_folder);
    check_existence(SCRIPT_PATH);

    std::wstring exe_name_(L"pythonw.exe");
    std::wstring application_name_ = emb_folder + L"\\" + exe_name_;
    std::wstring command_line_      = exe_name_ + L" " + SCRIPT_PATH;

    check_existence(application_name_);

    STARTUPINFO info = {sizeof(info)};
    PROCESS_INFORMATION processInfo;
    if (CreateProcess(
            (wchar_t*)application_name_.c_str(),
            (wchar_t*)command_line_.c_str(),
            NULL, NULL, TRUE, 0, NULL, NULL, &info, &processInfo))
    {
        ::WaitForSingleObject(processInfo.hProcess, INFINITE);
        CloseHandle(processInfo.hProcess);
        CloseHandle(processInfo.hThread);
    }
    return 0;
}
