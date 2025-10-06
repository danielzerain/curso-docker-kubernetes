package com.dzerain.tarea2.service;

import com.dzerain.tarea2.dto.Usuario;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;

@Service
public class UserServices {

  private List<Usuario> getUserList() {
    return List.of(
        new Usuario(1, "Wilson", "Perez", "wilson.perez@gmail.com"),
        new Usuario(2, "Maria", "Fuentes", "maria.fuentes@gmail.com"),
        new Usuario(3, "Pedro", "Morales", "pedro.morales@gmail.com"));
  }

  public List<Usuario> list() {
    return getUserList();
  }

  public Optional<Usuario> getUser(Integer id) {
    return getUserList().stream().filter(u -> u.id().equals(id)).findFirst();
  }
}
