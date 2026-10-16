from pathlib import Path
from typing import Any
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from PIL import ImageTk
from img_manager.img_manager import ImgManager
from PIL.ExifTags import IFD
from src.constants import (
    CANVAS_WIDTH,
    DELETE_ACTION,
    EDIT_ACTION,
    FILENAME_LABEL,
    LIST_ITEM_EXTRA_HEIGHT,
    MOUSE_WHEEL_DELTA,
    NO_EXIF_METADATA,
    PREVIEW_SIZE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class ListFrame(ttk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        img_list: list[ImgManager],
        item_height: int,
    ) -> None:
        super().__init__(master=parent)
        self.pack(expand=True, fill='both')

        self.tk_previews = []
        # widget data
        self.img_list = img_list
        self.item_number = len(img_list)
        self.list_height = self.item_number * (
            item_height + LIST_ITEM_EXTRA_HEIGHT
        )
        self.item_height = item_height

        # canvas
        self.canvas = tk.Canvas(
            self,
            yscrollincrement=item_height + LIST_ITEM_EXTRA_HEIGHT,
            scrollregion=(0, 0, CANVAS_WIDTH, self.list_height),
        )
        # self.canvas.configure(yscrollincrement=self.canvas.bbox('all'))
        self.canvas.pack(expand=True, fill='both')

        # display frame
        self.frame = ttk.Frame(self)

        for image in self.img_list:
            self.create_item(image).pack(
                expand=True,
                fill='both',
                padx=4,
                pady=10)
            ttk.Separator(
                self.frame,
                orient='horizontal').pack(expand=True, fill='x')

        # events
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

        self.bind('<Configure>', self._on_configure)

    def on_mousewheel(self, event: tk.Event) -> None:
        if event.num == 4:
            self.canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(
                -int(event.delta / MOUSE_WHEEL_DELTA),
                "units",
            )

    def _on_configure(self, event: tk.Event) -> None:
        if event.widget is self:
            self.update_size()

    def update_size(self) -> None:
        if self.list_height >= self.winfo_height():
            height = self.list_height
            self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
            self.canvas.bind_all("<Button-4>", self.on_mousewheel)
            self.canvas.bind_all("<Button-5>", self.on_mousewheel)
        else:
            height = self.winfo_height()
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

        self.canvas.create_window(
            (0, 0),
            window=self.frame,
            anchor='nw',
            width=self.winfo_width(),
            height=height
            )

    def create_item(self, image: ImgManager) -> ttk.Frame:
        frame = ttk.Frame(self.frame)

        # grid layout
        frame.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)
        frame.columnconfigure((0, 1, 2), weight=1, uniform='a')

        # widgets

        # image preview
        preview = ImageTk.PhotoImage(image.preview)
        self.tk_previews.append(preview)

        preview_frame = ttk.Frame(
            frame,
            width=PREVIEW_SIZE,
            height=PREVIEW_SIZE,
        )
        preview_frame.grid(row=1, column=0, rowspan=7, padx=10)

        # Prevent the frame from shrinking to fit its contents
        preview_frame.grid_propagate(False)

        preview_label = ttk.Label(preview_frame, image=preview)
        preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Non modifiable main data
        row = 1
        for label, value in image.primary_data.items():
            if label == FILENAME_LABEL:
                filename = Path(value).name
                ttk.Label(
                    frame,
                    borderwidth=1,
                    relief='raised',
                    text=f'File: {filename}',
                    anchor='center').grid(
                        row=0,
                        column=0,
                        columnspan=3,
                        sticky='',
                        pady=5,
                        ipady=2,
                        ipadx=2)
            else:
                ttk.Label(frame,
                          text=f'{label}: {value}').grid(
                              row=row,
                              column=1,
                              sticky='w')
                row += 1

        # Modifiable main EXIF data
        row = 1

        exif_menu = ttk.Menubutton(frame, text='Main Exif data')
        exif_menu.grid(row=row, column=2, sticky='ew', padx=5)
        menu = tk.Menu(exif_menu, tearoff=0)
        exif_menu.config(menu=menu)

        self.populate_exif_metadata(menu=menu, image=image)

        row += 1

        # Modifiable EXIF subdirectories
        for ifd_enum in image.get_formatted_exif_subdir():
            directory_menu = ttk.Menubutton(frame, text=f'{ifd_enum.name}')
            directory_menu.grid(row=row, column=2, sticky='ew', padx=5)
            menu = tk.Menu(directory_menu, tearoff=0)
            directory_menu.config(menu=menu)

            self.populate_exif_subdir(
                menu=menu,
                image=image,
                ifd_enum=ifd_enum,
            )
            row += 1

        return frame

    def edit_metadata(self,
                      pointer_id: int,
                      current_value: str,
                      image: ImgManager,
                      menu: tk.Menu,
                      directory: dict[str, dict[str, Any]] | None = None,
                      ifd_enum: IFD | None = None) -> None:

        proceed = messagebox.askokcancel(
            parent=self.frame,
            title="Are you sure?",
            message="Modifying the metadata could cause irreparable damage to \
the image, do you want to continue?")

        if not proceed:
            return

        action = simpledialog.askstring(
            parent=self.frame,
            title="Choose an action",
            prompt="Type the action you want to perform:\nEdit\nDelete",
            initialvalue='Edit'
            )

        if action is None:
            return

        if action.lower() == EDIT_ACTION:
            new_value = simpledialog.askstring(
                parent=self.frame,
                title="Edit metadata",
                prompt="Enter the new value:",
                initialvalue=current_value,
            )
            if new_value is None:
                return
        elif action.lower() == DELETE_ACTION:
            confirm = messagebox.askokcancel(
                parent=self.frame,
                title="Are you sure?",
                message="This action is irreversible, do you want to continue?"
                )
            if not confirm:
                return
        else:
            messagebox.showerror(
                parent=self.frame,
                title='Error!',
                message=f'Selected option not recognized: {action}')
            return

        try:
            if action.lower() == EDIT_ACTION:
                image.edit_exif_field(
                    new_data=new_value,
                    pointer_id=pointer_id,
                    ifd_enum=ifd_enum)

            elif action.lower() == DELETE_ACTION:
                image.delete_exif_field(
                    pointer_id=pointer_id,
                    ifd_enum=ifd_enum)

            if directory is None:
                self.populate_exif_metadata(menu=menu, image=image)
            else:
                self.populate_exif_subdir(
                    menu=menu,
                    image=image,
                    ifd_enum=ifd_enum,
                )

            messagebox.showinfo(
                parent=self.frame,
                title='Success!',
                message='The data has been modified successfully.')

        except (OSError, KeyError, ValueError) as error:
            messagebox.showerror(
                parent=self.frame,
                title='Error!',
                message=f"Could not modify the data, reason: {error}")

    def populate_exif_metadata(self, menu: tk.Menu, image: ImgManager) -> None:
        menu.delete(0, "end")

        data = image.get_formatted_exif_data()

        if not data:
            menu.add_command(label=NO_EXIF_METADATA)
            return

        for label, element in data.items():
            menu.add_command(
                label=f"{label}: {element['value']}",
                command=lambda e=element: self.edit_metadata(
                    pointer_id=e['id'],
                    image=image,
                    current_value=e['value'],
                    menu=menu
                    )
                )

    def populate_exif_subdir(
        self,
        image: ImgManager,
        menu: tk.Menu,
        ifd_enum: IFD,
    ) -> None:
        menu.delete(0, "end")

        dirs = image.get_formatted_exif_subdir()
        directory = dirs.get(ifd_enum)

        for label, element in directory.items():
            menu.add_command(
                label=f"{label}: {element['value']}",
                command=lambda e=element: self.edit_metadata(
                    pointer_id=e['id'],
                    image=image,
                    current_value=e['value'],
                    menu=menu,
                    directory=directory,
                    ifd_enum=ifd_enum
                    )
                )


def gui(image_list: list[ImgManager]) -> None:
    main_window = tk.Tk()
    main_window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    main_window.title('Scorpion')

    ListFrame(main_window, image_list, PREVIEW_SIZE)

    main_window.mainloop()
